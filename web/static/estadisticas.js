function generarespecificas(id_div_especificas, specific_stats) {
    let clasificadores = Object.keys(specific_stats);
    let datos_json = JSON.parse(specific_stats[clasificadores[0]]);
    let stats = Object.keys(datos_json);

    let div_especificas = document.querySelector("#" + id_div_especificas);

    // Crear selector para las estadísticas
    let select = document.createElement("select");
    select.setAttribute("id", "selector_stat");
    select.setAttribute("class", "form-select");
    select.style.width = "25%";
    select.style.margin = "auto";


    for (let i = 0; i < stats.length; i++) {
        let option = document.createElement("option");
        option.value = stats[i];
        option.text = stats[i];
        select.appendChild(option);
    }

    let id_div_estadisticas = "grafico_stat";
    select.addEventListener('change', (event) => {
        seleccionarstat(id_div_estadisticas, event.target.value, stats);
    });

    div_especificas.appendChild(select);

    let div_grafico = document.createElement("div");
    div_grafico.setAttribute("id", id_div_estadisticas);

    let div_checkboxes = document.createElement("div");
    div_checkboxes.setAttribute("id", "checkboxes_especifico_grafico_stat");

    div_especificas.appendChild(div_grafico);
    div_especificas.appendChild(div_checkboxes);

    generarcheckboxes_clasificadores("checkboxes_especifico_grafico_stat", id_div_estadisticas, clasificadores);
    generargraficoestadistico(id_div_estadisticas, null, clasificadores);

    let color = d3.scaleOrdinal()
        .domain(clasificadores)
        .range(d3.schemeCategory10);

    for (let i = 0; i < clasificadores.length; i++) {
        let datos_json = JSON.parse(specific_stats[clasificadores[i]]);

        for (let j = 0; j < stats.length; j++) {
            anadirestadistica(id_div_estadisticas, datos_json, stats[j], color, clasificadores[i]);
        }
    }

    seleccionarstat(id_div_estadisticas, stats[0], stats);

}

function seleccionarstat(id_div_estadisticas, stat_seleccionada, lista_stats) {
    let statsvg = d3.select("#" + id_div_estadisticas).select("svg").select("g");

    for (let i = 0; i < lista_stats.length; i++) {
        let pts = statsvg.selectAll('circle[stat='+ lista_stats[i] +']');
        let lineas = statsvg.selectAll('line[stat='+ lista_stats[i] +']');
        if (stat_seleccionada === lista_stats[i]){
            pts.filter(function(d) {
                return d[0] <= cont && comprobarvisibilidad(d3.select(this).attr("clf"),stat_seleccionada);
            })
                .style("visibility", "visible")

            lineas.filter(function (d) {
                return d <= cont && comprobarvisibilidad(d3.select(this).attr("clf"),stat_seleccionada);;
            })
                .style("visibility", "visible")
        }else{
            pts.style("visibility", "hidden");
            lineas.style("visibility", "hidden");
        }
    }

}

function habilitar_clasificador(id_div_objetivo, checked, clasificador) {
    let nombre_clasificador = clasificador
        .replace("(","")
        .replace(")","");
    let statsvg = d3.select("#" + id_div_objetivo).select("svg").select("g");
    let pts = statsvg.selectAll('circle[clf='+ nombre_clasificador +']');
    let lineas = statsvg.selectAll('line[clf='+ nombre_clasificador +']');

    if(checked){
        pts.filter(function(d) {
            return d[0] <= cont && comprobarvisibilidad(nombre_clasificador, d3.select(this).attr("stat"));
        })
            .style("visibility", "visible")

        lineas.filter(function (d) {
            return d <= cont && comprobarvisibilidad(nombre_clasificador, d3.select(this).attr("stat"));
        })
            .style("visibility", "visible")
    }else{
        pts.style("visibility", "hidden");
        lineas.style("visibility", "hidden");
    }
}

function generarcheckboxes_clasificadores(id_div_objetivo, id_div_estadisticas, clasificadores) {
    let div_objetivo = document.querySelector("#" + id_div_objetivo);

    for (let index in clasificadores){
        let clasificador = clasificadores[index];

        let input = document.createElement("input");
        input.setAttribute("id", "chk_" + clasificador.replace("(","")
            .replace(")",""));
        input.setAttribute("type", "checkbox");
        input.setAttribute("class", "form-check-input");
        input.checked = true;


        input.addEventListener("click", function() {
            habilitar_clasificador(id_div_estadisticas, this.checked, clasificador);
        });

        let label = document.createElement("label");
        label.setAttribute("for", "chk_" + clasificador.replace("(","")
            .replace(")",""));
        label.textContent = clasificador;

        div_objetivo.appendChild(input);
        div_objetivo.appendChild(label);
        div_objetivo.append(" ");
    }

}


function generargraficoestadistico(id_div_objetivo, datos_stats, dominio) {

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
        .domain(dominio)
        .range(d3.schemeCategory10);

    statsvg.append('g')
        .attr("id","leyenda")
        .selectAll("target")
        .data(dominio)
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
    if (datos_stats !== null) {
        for (let index in dominio) {
            anadirestadistica(id_div_objetivo, datos_stats, dominio[index], color);
        }
    }

}

function anadirestadistica(id_div, datos_stats, stat, color, clf="no") {
    let margin = {top: 10, right: 120, bottom: 40, left: 50},
        width = 950 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;

    let lista = crearListaStat(datos_stats, stat);

    let statsvg = d3.select("#" + id_div).select("svg").select("g");

    let statx = d3.scaleLinear()
        .domain([0, maxit])
        .range([0, width]);

    let staty = d3.scaleLinear()
        .domain([0, 1])
        .range([height, 0]);

    let nombre_clf = clf.replace("(","").replace(")","");

    let pts = statsvg.selectAll("dot")
        .data(lista)
        .enter()
        .append("circle")
        .attr("clf", nombre_clf)
        .attr("stat", stat)
        .attr("cx", function (d) {
            return statx(d[0]);
        })
        .attr("cy", function (d) {
            return staty(d[1]);
        })
        .attr("r", 5)
        .attr("fill", function () {
            if (clf === "no"){
                return color(stat);
            }else{
                return color(clf);
            }

        })
        .style("visibility", function (d) {
            if (d[0] <= cont) {
                return "visible";
            } else {
                return "hidden";
            }
        })

    for (let i = 0; i < lista.length - 1; i++) {
        statsvg.append("line")
            .data([i + 1])
            .attr("clf", nombre_clf)
            .attr("stat", stat)
            .attr("x1", statx(i))
            .attr("y1", staty(lista[i][1]))
            .attr("x2", statx(i + 1))
            .attr("y2", staty(lista[i + 1][1]))
            .attr("stroke", function () {
                if (clf === "no"){
                    return color(stat);
                }else{
                    return color(clf);
                }
            })
            .attr("stroke-width", 1.5)
            .style("visibility", function (d) {
                if (d < cont) {
                    return "visible";
                } else {
                    return "hidden";
                }
            })
    }

    let lineas = statsvg.selectAll('line[clf=' + nombre_clf + '][stat=' + stat + ']');

    document.addEventListener('next', next);
    document.addEventListener('prev', prev);


    function next() {
        pts.filter(function (d) {
            return d[0] === cont && comprobarvisibilidad(nombre_clf, stat);
        })
            .style("opacity", 0)
            .transition()
            .duration(600)
            .style("opacity", 1)
            .style("visibility", "visible");

        lineas.filter(function (d) {
            return d === cont && comprobarvisibilidad(nombre_clf, stat);
        })
            .attr("stroke-width", 0)
            .transition()
            .duration(600)
            .attr("stroke-width", 1)
            .style("visibility", "visible");

    }

    function prev() {
        pts.filter(function (d) {
            return d[0] > cont;
        })
            .style("visibility", "hidden");

        lineas.filter(function (d) {
            return d > cont;
        })
            .style("visibility", "hidden");
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

function comprobarvisibilidad(clasificador, stat) {
    let check = document.getElementById("chk_" + clasificador);
    let select = document.getElementById("selector_stat");

    if (check === null){ //Estadísticas generales
        console.log("ddd");
        return true;
    }else{
        if (check.checked && select.value === stat){
            return true;
        }
    }
    return false;
}