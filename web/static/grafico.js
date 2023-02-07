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

            binding();

            // Marcar los de la iteración 0
            svg.selectAll("circle")
                .filter(function(d) {
                    return d[3] === 0;})
                .style("stroke","yellow");


        }
    }

    xhr.open("POST", rutadatos);
    let parametros = new FormData();
    elementos.forEach(el => {
        parametros.append(el.nombre,el.valor)
    });
    xhr.send(parametros);

}

function STpreparardataset(datos) {
    let dataset = [];
    let xs = datos[cx];
    let ys = datos[cy];
    let etiq = datos['target'];
    let iter = datos['iter'];

    for (const key in xs){
        dataset.push([xs[key],ys[key],etiq[key],iter[key]])
    }

    return dataset;
}

function CTpreparardataset(datos) {
    let dataset = [];
    let xs = datos[cx];
    let ys = datos[cy];
    let etiq = datos['target'];
    let iter = datos['iter'];
    let clfs = datos['clf'];

    for (const key in xs){
        dataset.push([xs[key],ys[key],etiq[key],iter[key],clfs[key]])
    }

    return dataset;
}

function STdatabinding(){
    svg.append('g')
        .selectAll("dot")
        .data(dataset)
        .enter()
        .append("circle")
        .attr("cx", function (d) { return x(d[0]); } )
        .attr("cy", function (d) { return y(d[1]); } )
        .attr("r", 3)
        .style("fill", function (d) {
            if (d[3] <= cont) {
                return color(d[2]);
            } else {
                return "grey";
            }
        });

}

function CTdatabinding(){
    svg.append('g')
        .selectAll("dot")
        .data(dataset)
        .enter()
        .append(function (d) {return forma(d)});

    // Marcar los de la iteración 0
    svg.selectAll("rect")
        .filter(function(d) {
            return d[3] === 0;})
        .style("stroke","yellow");
}

function forma(d){
    var svgns = "http://www.w3.org/2000/svg";
    let c = () =>{
        if (d[3] <= cont) {
            return color(d[2]);
        } else {
            return "grey";
        }
    };

    var forma = document.createElementNS(svgns, "rect");
    forma.setAttributeNS(null, "x", x(d[0]));
    forma.setAttributeNS(null, "y", y(d[1]));
    forma.setAttributeNS(null, "width", 5);
    forma.setAttributeNS(null, "height",5);
    forma.setAttributeNS(null, "fill", c());

    return forma;
}

let nexit = d3.select("#nextit");
nexit.on("click", next);

function next(){
    if (cont < maxit){
        cont++;
        svg.selectAll("circle")
            .filter(function(d) {
                return d[3] === cont;
            })
            .style("fill", function(d){ return color(d[2]);})
            .transition()
            .duration(300)
            .attr("r", 5)
            .transition()
            .duration(300)
            .attr("r", 3);
        actualizaProgreso();
    }
}



let previt = d3.select("#previt");
previt.on("click", prev);

function prev(){
    if (cont > 0){
        cont--;
        svg.selectAll("circle")
            .filter(function(d) {
                return d[3] > cont;
            })
            .style("fill", "grey");
        actualizaProgreso();
    }
}

let rep = d3.select("#reproducir")
rep.on("click",reproducir);

function reproducir(){
    // Si vuelve a clickar que pare
    var intervalo = setInterval(function () {
        if (cont >= maxit){
            clearInterval(intervalo);
        }
        next();
    }, 750)
}

function actualizaProgreso(){
    document.getElementById("progreso").value=cont;
    document.getElementById("iteracion").innerHTML = cont;
}