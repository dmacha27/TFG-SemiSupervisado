let dataset = [];

let margin = {top: 10, right: 30, bottom: 30, left: 60},
    width = 800 - margin.left - margin.right,
    height = 670 - margin.top - margin.bottom;

let svg, x, y, maxit;

let xhr = new XMLHttpRequest();
xhr.onreadystatechange = function () {
    if (this.readyState === XMLHttpRequest.DONE) {
        let datos = JSON.parse(xhr.responseText);
        let carga = document.getElementById("cargando");
        carga.style.visibility = 'hidden';
        carga.style.opacity = '0';
        carga.style.height = '0';

        let controles = document.getElementById("controles");
        controles.style.visibility = 'visible';

        dataset = preparardataset(datos);
        maxit = d3.max(dataset, d => d[3]);

        svg = d3.select("#semisupervisedchart")
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
            .style("display", "block")
            .style("margin", "auto");

        x = d3.scaleLinear()
            .domain([d3.min(dataset, d => d[0]), d3.max(dataset, d => d[0])])
            .range([ 0, width ]);

        y = d3.scaleLinear()
            .domain([d3.min(dataset, d => d[1]), d3.max(dataset, d => d[1])])
            .range([ height, 0]);

        svg.append("g")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(x));
        svg.append("g")
            .call(d3.axisLeft(y));

        chartdatabinding()
    }
}
xhr.open("POST","/selftrainingd");
var parametros= new FormData()
parametros.append("n", n)
parametros.append("th", th)
parametros.append("n_iter", n_iter )
parametros.append("target", target)
xhr.send(parametros);

let cont = 0;

function preparardataset(datos) {
    let dataset = [];
    let xs = datos['C1'];
    let ys = datos['C2'];
    let etiq = datos['target'];
    let iter = datos['iter']


    for (const key in xs){
        dataset.push([xs[key],ys[key],etiq[key],iter[key]])
    }

    return dataset;
}


function chartdatabinding(){
    svg.append('g')
        .selectAll("dot")
        .data(dataset)
        .enter()
        .append("circle")
        .attr("cx", function (d) { return x(d[0]); } )
        .attr("cy", function (d) { return y(d[1]); } )
        .attr("r", 2)
        .style("fill", function (d) {
            if (d[3] <= cont) {
                if (d[2] === 0) {
                    return "blue";
                } else if (d[2] === 1) {
                    return "red";
                } else{
                    return "green";
                }
            } else {
                return "grey";
            }
        })
}

let nexit = d3.select("#nextit");

function next(){
    if (cont < maxit){
        cont++;
        chartdatabinding()
    }
}

nexit.on("click", next);

let previt = d3.select("#previt");

function prev(){
    if (cont > 0){
        cont--;
        chartdatabinding()
    }
}

previt.on("click", prev);