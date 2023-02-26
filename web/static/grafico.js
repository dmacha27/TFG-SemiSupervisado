const nexit = d3.select("#nextit");
const previt = d3.select("#previt");
const rep = d3.select("#reproducir");
const simbolos = d3.symbol();

let graficosvg, gx, gy, maxit, color, mapa;

function inicializarGrafico(datos, preparar, binding) {
    let margin = {top: 80, right: 90, bottom: 60, left: 45},
    width = 850 - margin.left - margin.right,
    height = 700 - margin.top - margin.bottom;


    let dataset = preparar(JSON.parse(datos.log));
    mapa = JSON.parse(datos.mapa);
    maxit = d3.max(dataset, d => d[3]);
    document.getElementById("progreso").max = maxit;

    color = d3.scaleOrdinal()
        .domain(Object.keys(mapa))
        .range(d3.schemeCategory10);

    graficosvg = d3.select("#semisupervisedchart")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
        .style("display", "block")
        .style("margin", "auto");

    //Etiqueta eje X
    graficosvg.append("text")
        .attr("class", "cx")
        .attr("text-anchor", "middle")
        .attr("x", width / 2)
        .attr("y", height + margin.bottom / 2)
        .text(cx);

    //Etiqueta eje Y
    graficosvg.append("text")
        .attr("class", "cy")
        .attr("text-anchor", "middle")
        .attr("y", -margin.left)
        .attr("x", -height / 2)
        .attr("dy", "1em")
        .attr("transform", "rotate(-90)")
        .text(cy);

    //Leyenda
    graficosvg.append('g')
        .attr("id","leyenda")
        .selectAll("target")
        .data(Object.keys(mapa))
        .enter()
        .append("text")
        .attr("x", 120)
        .attr("y", function(d,i){ return 100 + i*25;})
        .style("fill", function(d){ return color(parseInt(d));})
        .text(function(d){ return mapa[d];})
        .style("alignment-baseline", "middle")
        .attr("transform", "translate(" + (width -110) + "," + -120 + ")");

    // Nombre del dataset
    graficosvg.append("text")
        .attr("x", width/2)
        .attr("y", -margin.top/2)
        .attr("text-anchor", "middle")
        .style("font-size", "16px")
        .text(traducir('Dataset') + ": " + fichero);


    gx = d3.scaleLinear()
        .domain([d3.min(dataset, d => d[0]), d3.max(dataset, d => d[0])])
        .range([0, width]);

    gy = d3.scaleLinear()
        .domain([d3.min(dataset, d => d[1]), d3.max(dataset, d => d[1])])
        .range([height, 0]);

    graficosvg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(gx));
    graficosvg.append("g")
        .call(d3.axisLeft(gy));

    //Basado en https://d3-graph-gallery.com/graph/interactivity_tooltip.html#template
    d3.select("#semisupervisedchart")
        .append("div")
        .style("opacity", 0)
        .attr("class", "tooltip")
        .style("background-color", "white")
        .style("border", "solid")
        .style("border-width", "2px")
        .style("border-radius", "5px")
        .style("padding", "5px")
        .style("position", "absolute")

    binding(dataset);

}

const mouseover = function (d) {
    d3.select(".tooltip")
        .style("opacity", 1)
        .style("opacity", 1)

};

const mouseleave = function (d) {
    d3.select(".tooltip")
        .style("stroke", "none")
        .style("opacity", 0)
};

function actualizaProgreso(paso){
    document.getElementById("progreso").value=cont;
    document.getElementById("iteracion").innerHTML = cont;
    if (paso === "next"){
        document.dispatchEvent(new Event('next'));
    }else{
        document.dispatchEvent(new Event('prev'));
    }
}

let intervalo = null;
function reproducir(){
    if (!intervalo){
        document.getElementById("reproducir").innerHTML = traducir('Pause');
        intervalo = setInterval(function () {
            if (cont >= maxit){
                document.getElementById("reproducir").innerHTML = traducir('Play');
                clearInterval(intervalo);
                intervalo = null;
            }
            next();
        }, 750)
    } else {
        document.getElementById("reproducir").innerHTML = traducir('Play');
        clearInterval(intervalo);
        intervalo = null;
    }
}