
function estadisticagenerica(stats) {

    let margin = {top: 10, right: 120, bottom: 40, left: 50},
        width = 950 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;


    let statsvg = d3.select("#graficoestadisticas")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
        .style("display", "block")
        .style("margin", "auto");

    let statx = d3.scaleLinear()
        .domain([0, maxit])
        .range([0, width]);

    let staty = d3.scaleLinear()
        .domain([0, 1])
        .range([height, 0]);

    statsvg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(statx));
    statsvg.append("g")
        .call(d3.axisLeft(staty));

    //Etiqueta eje X
    statsvg.append("text")
        .attr("class", "cx")
        .attr("text-anchor", "middle")
        .attr("x", width / 2)
        .attr("y", height + margin.bottom)
        .text(traducir('Iteration'));

    //Etiqueta eje Y
    statsvg.append("text")
        .attr("class", "cy")
        .attr("text-anchor", "middle")
        .attr("y", -margin.left)
        .attr("x", -height / 2)
        .attr("dy", "1em")
        .attr("transform", "rotate(-90)")
        .text(traducir('Rate'));

    let color = d3.scaleOrdinal()
        .domain(stats)
        .range(d3.schemeCategory10);

    statsvg.append('g')
        .attr("id","leyenda")
        .selectAll("target")
        .data(stats)
        .enter()
        .append("text")
        .attr("x", 120)
        .attr("y", function(d,i){ return 100 + i*25;})
        .style("fill", function(d){ return color(d);})
        .text(function(d){ return d;})
        .style("alignment-baseline", "top")
        .attr("transform", "translate(" + (width -110) + "," + -90 + ")");

    return color
}

function anadirestadistica(datos, stat, color) {
    let lista = crearListaStat(JSON.parse(datos.stats),stat);

    let margin = {top: 10, right: 30, bottom: 40, left: 60},
        width = 850 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;

    let statsvg = d3.select("#graficoestadisticas").select("svg").select("g");

    let statx = d3.scaleLinear()
        .domain([0, maxit])
        .range([0, width]);

    let staty = d3.scaleLinear()
        .domain([0, 1])
        .range([height, 0]);

    let pts = statsvg.selectAll("dot")
        .data(lista)
        .enter()
        .append("circle")
        .attr("id", stat)
        .attr("cx", function (d) { return statx(d[0]); } )
        .attr("cy", function (d) { return staty(d[1]); } )
        .attr("r", 5)
        .attr("fill", color(stat))
        .style("visibility", function (d) {
            if (d[0] <= cont && comprobarvisibilidad(stat)){
                return "visible";
            }else{
                return "hidden";
            }
        })

    for (let i = 0; i < lista.length - 1; i++) {
        statsvg.append("line")
            .data([i+1])
            .attr("id", stat)
            .attr("x1", statx(i))
            .attr("y1", staty(lista[i][1]))
            .attr("x2", statx(i + 1))
            .attr("y2", staty(lista[i + 1][1]))
            .attr("stroke", color(stat))
            .attr("stroke-width", 1.5)
            .style("display", function (d) {
                if (d < cont && comprobarvisibilidad(stat)){
                    return "block";
                }else{
                    return "none";
                }
            })
    }

    let lineas = statsvg.selectAll('line[id='+stat+']');

    document.addEventListener('next', next);
    document.addEventListener('prev', prev);


    function next() {
        if(comprobarvisibilidad(stat)) {
            pts.filter(function (d) {
                return d[0] === cont;
            })
                .style("opacity", 0)
                .transition()
                .duration(600)
                .style("opacity", 1)
                .style("visibility", "visible")

            lineas.filter(function (d) {
                return d === cont;
            })
                .attr("stroke-width", 0)
                .transition()
                .duration(600)
                .attr("stroke-width", 1.5)
                .style("display", "block");
        }
    }

    function prev() {
        pts.filter(function(d) {
            return d[0] > cont;
        })
            .style("visibility", "hidden")

        lineas.filter(function (d) {
            return d > cont;
        })
            .style("display", "none");
    }
}


function crearListaStat(stats,stat){
    let lista = [];
    let aux = stats[stat.toLowerCase()];

    for (let i = 0; i <= maxit; i++) {
        lista.push([i,aux[i]]);
    }

    return lista;
}

function habilitar(checked,stat) {
    let statsvg = d3.select("#graficoestadisticas").select("svg").select("g");
    let pts = statsvg.selectAll('circle[id='+stat+']');
    let lineas = statsvg.selectAll('line[id='+stat+']');
    if(checked){
        pts.filter(function(d) {
            return d[0] <= cont;
        })
            .style("visibility", "visible")

        lineas.filter(function (d) {
            return d <= cont;
        })
            .style("display", "block");
    }else{
        pts.style("visibility", "hidden")
        lineas.style("display", "none");
    }
}

function comprobarvisibilidad(stat) {
    let check = document.getElementById("chk_" + stat);
    return check.checked;
}