#!/usr/bin/env julia

using Pkg
Pkg.activate(joinpath(@__DIR__, "..", "TDA"))

using Distances
using LinearAlgebra
using Ripserer
using NPZ
using Statistics

function load_data(filename)
    path = abspath(joinpath(@__DIR__, "..", "data", filename))
    data = npzread(path)
    words = collect(keys(data))
    vecs = [data[word] for word in words]
    (words, hcat(vecs...)')
end

function calculate_persistent_holes(points, words; dim=1, quant=0.01)
    dist_matrix = pairwise(CosineDist(), points, dims=1)
    
    min_thr = 1e-10
    dist_matrix[dist_matrix .< min_thr] .= min_thr
    dist_matrix[diagind(dist_matrix)] .= 0.0
    dist_matrix[diagind(dist_matrix)] .= min_thr / 2
            
    diagram = ripserer(dist_matrix, dim_max=dim, alg=:involuted, reps=true)
    holes = diagram[dim+1]
            
    total_holes = length(holes)
    top = ceil(Int, total_holes * quant)
    top_holes = holes[end-min(end-1, top-1):end]
    
    results = map(reverse(top_holes)) do hole
        indices = Int[]
        
        repr = hole.representative
        for elem in repr.elements
            verts = Ripserer.vertices(elem)
            append!(indices, verts .+ 1)
        end
                  
        indices = unique(indices)
                
        (
            persistence = hole.death - hole.birth,
            birth = hole.birth,
            death = hole.death,
            words = words[indices],
            vectors = points[indices, :],
            centroid = Statistics.mean(points[indices, :], dims=1)[1, :],
            size = length(indices)
        )
    end
    
    (total_holes=total_holes, top_holes=results)
end

function show_results(results)    
    println("Всего дырок ", results.total_holes)
    println("Топ ", length(results.top_holes), " самых устойчивых (1%):")

    for (i, hole) in enumerate(results.top_holes)
        println("\nНомер дырки: ", i)
        println("Размер: ", hole.size)
        println("Устойчивость: ", round(hole.persistence, digits=4))
        println("Диапазон: [", round(hole.birth, digits=4), ", ", round(hole.death, digits=4), "]")
        println("Леммы: ", join(hole.words, ", "))
        println("Центроид: ", round.(hole.centroid, digits=4))
        println("Эмбеддинги:")
        for (word, vec) in zip(hole.words, eachrow(hole.vectors))
            println("  ", word, ": ", round.(vec, digits=4))
        end
    end
end

function main(filename; dim=1, quant=0.01)
    words, points = load_data(filename)
    results = calculate_persistent_holes(points, words; 
                dim=dim, quant=quant)
    show_results(results)
    return results
end

results = main("adyghe_dict.npz", dim=1, quant=0.01)
