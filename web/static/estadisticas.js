function generarespecificas(id_div_especificas, specific_stats) {
    let clasificadores = Object.keys(specific_stats);

    let div_especificas = document.querySelector("#" + id_div_especificas);

    // Crear selector para los algoritmos
    let select = document.createElement("select");
    select.setAttribute("id", "selector_clasificador");
    select.setAttribute("class", "form-select");
    select.style.width = "25%";
    select.style.margin = "auto";


    for (let i = 0; i < clasificadores.length; i++) {
        let option = document.createElement("option");
        option.value = clasificadores[i];
        option.text = clasificadores[i];
        select.appendChild(option);
    }

    select.addEventListener('change', (event) => {
        seleccionarclasificador(event.target.value, clasificadores);
    });

    div_especificas.appendChild(select);

    //Crear los contenedores donde irá cada gráfico específico
    for (let i = 0; i < clasificadores.length; i++) {
        let nombre_clasificador = clasificadores[i]
            .replace("(","")
            .replace(")","");

        let div = document.createElement("div");
        div.setAttribute("id", nombre_clasificador);
        div.style.display = "none";

        let div_especifico = document.createElement("div");
        div_especifico.setAttribute("id", "especifico_" + nombre_clasificador);

        let div_checkboxes = document.createElement("div");
        div_checkboxes.setAttribute("id", "checkboxes_especifico_" + nombre_clasificador);
        div.appendChild(div_especifico);
        div.appendChild(div_checkboxes);

        div_especificas.appendChild(div);

    }

    for (let i = 0; i < clasificadores.length; i++) {
        let nombre_clasificador = clasificadores[i]
            .replace("(","")
            .replace(")","");

        let id_div_especifico = "especifico_" + nombre_clasificador;
        let id_div_checkboxes = "checkboxes_especifico_" + nombre_clasificador;

        let datos_json = JSON.parse(specific_stats[clasificadores[i]]);
        let stats = Object.keys(datos_json);

        generarcheckboxes(id_div_checkboxes, id_div_especifico, stats)
        generargraficoestadistico(id_div_especifico, datos_json, stats)
    }

    seleccionarclasificador(clasificadores[0], clasificadores);

}

function seleccionarclasificador(clasificador_seleccionado, lista_clasificadores) {

    for (let i = 0; i < lista_clasificadores.length; i++) {
        let nombre_clasificador = lista_clasificadores[i]
            .replace("(","")
            .replace(")","");
        let div = document.querySelector("#" + nombre_clasificador);
        if (clasificador_seleccionado === lista_clasificadores[i]){
            div.style.display = "block";
        }else{
            div.style.display = "none";
        }
    }

}

function generarcheckboxes(id_div_objetivo, id_div_estadisticas, stats) {
    let div_objetivo = document.querySelector("#" + id_div_objetivo);

    for (let index in stats){
        let stat = stats[index];

        let input = document.createElement("input");
        input.setAttribute("id", "chk_" + id_div_estadisticas + "_" + stat);
        input.setAttribute("type", "checkbox");
        input.setAttribute("class", "form-check-input");
        if (index === "0"){
            input.checked = true;
        }

        input.addEventListener("click", function() {
            habilitar(id_div_estadisticas, this.checked, stat);
        });

        let label = document.createElement("label");
        label.setAttribute("for", "chk_" + id_div_estadisticas + "_" + stat);
        label.textContent = stat;

        div_objetivo.appendChild(input);
        div_objetivo.appendChild(label);
        div_objetivo.append(" ");
    }

}


function generargraficoestadistico(id_div_objetivo, datos_stats, stats) {

    let margin = {top: 10, right: 120, bottom: 40, left: 50},
        width = 950 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;

    let statsvg = d3.select("#" + id_div_objetivo)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
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


    // Con el gráfico creado se dibuja cada estadística
    // vinculando los eventos
    for (let index in stats){
        anadirestadistica(id_div_objetivo, datos_stats, stats[index], color);
    }

}

function anadirestadistica(id_div_objetivo, datos_stats, stat, color) {
    let margin = {top: 10, right: 120, bottom: 40, left: 50},
        width = 950 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;

    let lista = crearListaStat(datos_stats, stat);

    let statsvg = d3.select("#" + id_div_objetivo).select("svg").select("g");

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
        .attr("id", id_div_objetivo + "_" + stat)
        .attr("cx", function (d) {
            return statx(d[0]);
        })
        .attr("cy", function (d) {
            return staty(d[1]);
        })
        .attr("r", 5)
        .attr("fill", color(stat))
        .style("visibility", function (d) {
            if (d[0] <= cont && comprobarvisibilidad(id_div_objetivo, stat)) {
                return "visible";
            } else {
                return "hidden";
            }
        })

    for (let i = 0; i < lista.length - 1; i++) {
        statsvg.append("line")
            .data([i + 1])
            .attr("id", id_div_objetivo + "_" + stat)
            .attr("x1", statx(i))
            .attr("y1", staty(lista[i][1]))
            .attr("x2", statx(i + 1))
            .attr("y2", staty(lista[i + 1][1]))
            .attr("stroke", color(stat))
            .attr("stroke-width", 1.5)
            .style("display", function (d) {
                if (d < cont && comprobarvisibilidad(id_div_objetivo, stat)) {
                    return "block";
                } else {
                    return "none";
                }
            })
    }

    let lineas = statsvg.selectAll('line[id=' + id_div_objetivo + '_' + stat + ']');

    document.addEventListener('next', next);
    document.addEventListener('prev', prev);


    function next() {
        if (comprobarvisibilidad(id_div_objetivo, stat)) {
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
                .attr("stroke-width", 1)
                .style("display", "block");
        }
    }

    function prev() {
        pts.filter(function (d) {
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
    let aux = stats[stat];

    for (let i = 0; i <= maxit; i++) {
        lista.push([i,aux[i]]);
    }

    return lista;
}

function habilitar(id_div_objetivo, checked, stat) {
    let statsvg = d3.select("#" + id_div_objetivo).select("svg").select("g");
    let pts = statsvg.selectAll('circle[id='+ id_div_objetivo + '_' + stat +']');
    let lineas = statsvg.selectAll('line[id='+ id_div_objetivo + '_' + stat +']');

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

function comprobarvisibilidad(id_div_objetivo, stat) {
    let check = document.getElementById("chk_" + id_div_objetivo + "_" + stat);
    return check.checked;
}