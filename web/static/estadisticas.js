
function precision() {

    let lista = crearlista(JSON.parse(datos.stats),"precision");

    let margin = {top: 10, right: 30, bottom: 30, left: 60},
        width = 460 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;


    let precisionsvg = d3.select("#precision")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
        .style("display", "block")
        .style("margin", "auto");

    precisionx = d3.scaleLinear()
        .domain([0, maxit])
        .range([0, width]);

    precisiony = d3.scaleLinear()
        .domain([0, 1])
        .range([height, 0]);

    precisionsvg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(precisionx));
    precisionsvg.append("g")
        .call(d3.axisLeft(precisiony));

    let pts = precisionsvg.selectAll("dot")
        .data(lista)
        .enter()
        .append("circle")
        .attr("cx", function (d) { return precisionx(d[0]); } )
        .attr("cy", function (d) { return precisiony(d[1]); } )
        .attr("r", 5)
        .attr("fill", "#69b3a2")
        .style("visibility", function (d) {
            if (d[0] <= cont){
                return "visible";
            }else{
                return "hidden";
            }
        })
    console.log(pts)
    for (let i = 0; i < lista.length - 1; i++) {
        let linea = precisionsvg.append("line")
            .data([i+1])
            .attr("id", "nueva")
            .attr("x1", precisionx(i))
            .attr("y1", precisiony(lista[i][1]))
            .attr("x2", precisionx(i + 1))
            .attr("y2", precisiony(lista[i + 1][1]))
            .attr("stroke", "#69b3a2")
            .attr("stroke-width", 1.5)
            .style("visibility", "hidden");
    }

    let lineas = precisionsvg.selectAll('line[id="nueva"]');


    console.log(lineas);
    document.addEventListener('Iteracion', function (){
        next();
        prev();
    })

    function next() {
        pts.filter(function(d) {
            return d[0] === cont;
        })
            .style("visibility", "visible")

        lineas.filter(function (d) {
            return d === cont;
        })
            .style("visibility", "visible");


    }

    function prev() {
        pts.filter(function(d) {
            return d[0] > cont;
        })
            .style("visibility", "hidden")

        lineas.filter(function (d) {
            return d > cont;
        })
            .style("visibility", "hidden");
    }

}


function crearlista(stats,stat){
    let lista = [];
    let aux = stats[stat];

    for (let i = 0; i <= maxit; i++) {
        lista.push([i,aux[i]]);
    }

    return lista;
}