let datos, dataset = [];
let mapa;

let margin = {top: 50, right: 5, bottom: 60, left: 60},
    width = 900 - margin.left - margin.right,
    height = 700 - margin.top - margin.bottom;

let svg, x, y, maxit, color;
let cont = 0;

function inicializarGrafico(rutadatos, elementos, preparar, binding) {

    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE) {
            datos = JSON.parse(xhr.responseText);
            document.getElementById("div_cargando").remove();

            let controles = document.getElementById("controles");
            controles.style.visibility = 'visible';


            dataset = preparar(JSON.parse(datos.log));
            mapa = JSON.parse(datos.mapa);
            maxit = d3.max(dataset, d => d[3]);
            document.getElementById("progreso").max = maxit;

            color = d3.scaleOrdinal()
                .domain(Object.keys(mapa))
                .range(d3.schemeCategory10);

            svg = d3.select("#semisupervisedchart")
                .append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
                .style("display", "block")
                .style("margin", "auto");

            //Etiqueta eje X
            svg.append("text")
                .attr("class", "cx")
                .attr("text-anchor", "end")
                .attr("x", width / 2)
                .attr("y", height + margin.bottom / 2)
                .text(cx);

            //Etiqueta eje Y
            svg.append("text")
                .attr("class", "cy")
                .attr("text-anchor", "end")
                .attr("y", -margin.left)
                .attr("x", -height / 2)
                .attr("dy", "1em")
                .attr("transform", "rotate(-90)")
                .text(cy);

            //Leyenda
            svg.append('g')
                .selectAll("target")
                .data(Object.keys(mapa))
                .enter()
                .append("text")
                .attr("x", 120)
                .attr("y", function(d,i){ return 100 + i*25;})
                .style("fill", function(d){ return color(parseInt(d));})
                .text(function(d){ return mapa[d];})
                .attr("text-anchor", "left")
                .style("alignment-baseline", "middle");

            // Nombre del dataset
            svg.append("text")
                .attr("x", width/2)
                .attr("y", -margin.top/2)
                .attr("text-anchor", "middle")
                .style("font-size", "16px")
                .text("Dataset: " + fichero);


            x = d3.scaleLinear()
                .domain([d3.min(dataset, d => d[0]), d3.max(dataset, d => d[0])])
                .range([0, width]);

            y = d3.scaleLinear()
                .domain([d3.min(dataset, d => d[1]), d3.max(dataset, d => d[1])])
                .range([height, 0]);

            svg.append("g")
                .attr("transform", "translate(0," + height + ")")
                .call(d3.axisBottom(x));
            svg.append("g")
                .call(d3.axisLeft(y));

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

            binding();


        }
    }

    xhr.open("POST", rutadatos);
    let parametros = new FormData();
    elementos.forEach(el => {
        parametros.append(el.nombre,el.valor)
    });
    xhr.send(parametros);

}

const mouseover = function (d) {
    d3.select(".tooltip")
        .style("opacity", 1)
    d3.select(this)
        .style("stroke", "black")
        .style("opacity", 1)
};

const mouseleave = function (d) {
    d3.select(".tooltip")
        .style("opacity", 0)
    d3.select(this)
        .style("stroke", "none")
        .style("opacity", 0.8)
};


let nexit = d3.select("#nextit");
let previt = d3.select("#previt");
let rep = d3.select("#reproducir")


function actualizaProgreso(){
    document.getElementById("progreso").value=cont;
    document.getElementById("iteracion").innerHTML = cont;
}

let intervalo = null;
function reproducir(){
    if (!intervalo){
        document.getElementById("reproducir").innerHTML = "Pausar";
        intervalo = setInterval(function () {
            if (cont >= maxit){
                document.getElementById("reproducir").innerHTML = "Reproducir";
                clearInterval(intervalo);
                intervalo = null;
            }
            next();
        }, 750)
    } else {
        document.getElementById("reproducir").innerHTML = "Reproducir";
        clearInterval(intervalo);
        intervalo = null;
    }
}