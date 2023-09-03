//change to true for init options
let show_unclassified = true;

//default value for k_mer_threshold
let k_mer_threshold = 0.5;

//set after init when df is given
let all_species_list = [];
let unchecked_all = false;
let checked_all = true;

// categories colors:
blue_color = "#2563eb" // blue-600 in tailwind
orange_color = "#f59e0b" // amber-500 in tailwind

bar_chart = new Chart('bar_chart', {
    type: "bar",
    data: {},
    options: {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Chart.js Bar Chart'
      }
    }
  }
});


function updateBarPlot(genomes_data, index){
    let labels = []
    let data = []
    Object.keys(genomes_data).forEach((key) => {
        labels.push(key)
        data.push(genomes_data[key])
    });
    let datasets = [{
        data: data,
        borderColor: colors[index],
        backgroundColor: addAlpha(colors[index]),
        borderWidth: 2,
        borderRadius: Number.MAX_VALUE,
        borderSkipped: false,
    }]
    bar_chart.data.labels = labels
    bar_chart.data.datasets = datasets
    bar_chart.update()
}


function makeRadioButton(group, text, is_default, genomes_data, index) {
    var label = document.createElement("label")
    var radio = document.createElement("input")
    radio.type = "radio"
    radio.name = group
    radio.id = text
    //radio.group = group
    if (is_default) {
        radio.checked = "checked"
        updateBarPlot(genomes_data, index)
    }
    label.appendChild(radio)

    label.appendChild(document.createTextNode(text))
    label.addEventListener("click", (change) => {
        updateBarPlot(genomes_data, index)
    });
    return label;
}

const initResultsScript = (histogram_data, orthologous_data) => {
    const json_histogram_data = JSON.parse(histogram_data);
    const json_orthologous_data = JSON.parse(orthologous_data);
    runResultsScript(json_histogram_data, json_orthologous_data)
};

//set functions
//const update_species_list = (item) => {
//    is_changed = true;
//    if (item.checked) {
//        if (!species_list.includes(item.id)) {
//            species_list.push(item.id)
//        }
//    } else {
//        if (species_list.includes(item.id)) {
//            item_index = species_list.indexOf(item.id);
//            species_list.splice(item_index, 1);
//        }
//    }
//    document.getElementById("species_list_filter").value = [...species_list];
//}
//const update_k_mer_threshold = (new_val) => {
//    is_changed = true;
//    k_mer_threshold = new_val;
//    document.getElementById("k_mer_threshold").value = new_val;
//}
//
//

const addAlpha = (color) => {
    // coerce values so ti is between 0 and 1.
    const _opacity = Math.round(Math.min(Math.max(0.1 || 1, 0), 1) * 255);
    return color + _opacity.toString(16).toUpperCase();
}

const runResultsScript = (histogram_data, orthologous_data) => {
    console.log('inside runResultsScript')
    const radio_bar_plot_parameters = document.getElementById("parameters_option_bar_chart")
    Object.keys(histogram_data).forEach((key, index) => {
        var radio_btn = makeRadioButton("bar_plot_options", key, index === 0, histogram_data[key], index)
        radio_bar_plot_parameters.appendChild(radio_btn)
    });
    console.log(orthologous_data)
    var table = document.getElementById('ortologic_table');
    var headers_tr = document.createElement('tr');
    var th = document.createElement('th');
    var text = document.createTextNode('ortologic group');
    th.style.cssText = 'position:sticky; top:0; writing-mode:vertical-rl; background-color:white; z-index: 99;'; // = 'rotate(90.0deg)'
    th.appendChild(text)
    headers_tr.appendChild(th)
    Object.values(orthologous_data.columns).forEach((key, index) => {
        console.log(key, index)
        var th = document.createElement('th');
        var text = document.createTextNode(key);
        th.style.cssText = 'position:sticky; top:0; writing-mode:vertical-rl; background-color:white; z-index: 99;'
        th.appendChild(text)
        headers_tr.appendChild(th)
    });
    table.appendChild(headers_tr);
    
    Object.values(orthologous_data.index).forEach((key, index) => {
        var tr = document.createElement('tr');
        var th = document.createElement('th');
        th.style.position = 'sticky';
        th.style.left = '0';
        var text = document.createTextNode(key);
        th.appendChild(text)
        tr.appendChild(th)
        Object.values(orthologous_data.data[index]).forEach((key, index) => {
            var td = document.createElement('td');
            td.style.cssText = 'text-align:center;'
            if (key === 0){
                td.style.cssText += 'background-color:red;'
            } else if (key === 1){
                td.style.cssText += 'background-color:green;'
            }
            var text = document.createTextNode(key);
            td.appendChild(text);
            tr.appendChild(td);
        })
        table.appendChild(tr);
    })
    // document.body.appendChild(table);
    //datasets = json_data.map((val, idx) => {
    //    val.backgroundColor = addAlpha(colors[0])
    //    val.borderColor = colors[0]
    //    //val.fill = false
    //    return val
    //});
    //console.log('datasets', datasets)
    //bar_chart.data.datasets = datasets
    bar_chart.update()
}
//
//const createResultsCharts = () => {
//    bar_chart = new Chart('bar_chart', {
//        type: "bar",
//        data: {},
//        options: {}
//    });
//
//    pie_chart = new Chart('pie_chart', {
//        type: "doughnut",
//        data: {},
//        options: {}
//    });
//    return bar_chart, pie_chart;
//}
//
//const draw_species_pie_chart = (chart) => {
//    
//    const threshold_list = df.index.filter(item => item >= k_mer_threshold)
//
//    let sum_classified_df = df.loc({ rows: threshold_list, columns: species_list }).sum({axis: 0});
//
//    let sum_unclassified = sum_total - sum_classified_df.sum({axis: 1});
//
//    let unclassified_percent = (sum_unclassified/sum_total)*100
//    let classified_percent = 100 - (sum_unclassified/sum_total)*100
//
//    chart.data.labels = ["Percent to be retained","Percent to be filtered"]
//    let bins_colors = [blue_color, orange_color]
//    let bins_values = [unclassified_percent, classified_percent]
//    bins_values.push()
//
//    chart.data.datasets = [{
//        data: bins_values,
//        hoverOffset: 4,
//        backgroundColor: bins_colors
//        }
//    ];
//    chart.options.borderRadius = 10
//    chart.options.radius = "75%"
//    chart.options.plugins.legend.display = false;
//    chart.options.plugins.tooltip = {
//        titleFont: {
//            size: 24
//        },
//        bodyFont: {
//            size: 24
//        }
//    }
//
//    chart.update()
//}
//
//const draw_kmer_hist = (chart, pie_chart) => {
//    let sum_classified_df = df.loc({ columns: species_list }).sum({axis: 1});
//    let df_index = sum_classified_df.index;
//    sum_classified_df = sum_classified_df.setIndex(df_index)
//    const classified_indexes = sum_classified_df.index
//    const classified_values = classified_indexes.map((index) => {
//
//        return parseFloat(index) < k_mer_threshold ? 0 : sum_classified_df.loc([index]).values[0];
//    })
//    sum_classified_df = new dfd.Series(classified_values, { index: classified_indexes });
//    let sum_unclassified_df = sum_cols_df.sub(sum_classified_df)
//    const bins_x = df_index
//    const classified_y = sum_classified_df.values
//    const unclassified_y = sum_unclassified_df.values
//
//    
//    chart.data.labels = bins_x
//    chart.data.datasets = [
//        {
//            data: classified_y,
//            backgroundColor: orange_color,
//            label: 'Classified as contaminant'
//
//        }
//    ];
//    
//    show_unclassified ? chart.data.datasets.push({
//            data: unclassified_y,
//            backgroundColor: blue_color,
//            label: 'Classified as non-contaminant'
//        }) : null;
//
//
//    chart.options = {
//        onHover:(event, chartElem) => {
//            event.native.target.style.cursor = chartElem[0] ? "pointer" : "default";
//        },
//        onClick: (event) => { 
//
//            const xTop = chart.chartArea.left;
//            const xBottom = chart.chartArea.right;
//            const xMin = chart.scales.x.min;
//            const xMax = chart.scales.x.max;
//            let newX = 0;
//
//            if (event.x <= xBottom && event.x >= xTop) {
//                newX = Math.abs((event.x - xTop) / (xBottom - xTop));
//                newX = newX * (Math.abs(xMax - xMin)) + xMin;
//            };
//            update_k_mer_threshold(newX);
//            
//            draw_species_list();
//            if (unchecked_all || checked_all) {
//                let selection_flag = unchecked_all ? false : true;
//                set_selection(selection_flag);
//            } else {
//                draw_kmer_hist(chart, pie_chart);
//                draw_species_pie_chart(pie_chart);    
//            }
//
//        },
//        plugins: {
//            annotation: {
//                annotations: {
//                    line: {
//                        type: 'line',
//                        scaleID: 'x',
//                        value: parseFloat(k_mer_threshold),
//                        borderColor: 'rgb(255, 99, 132)',
//                        borderWidth: 2,
//                    }
//                }
//            },
//            legend: {
//                display: false
//            },
//            tooltip: {
//                titleFont: {
//                    size: 24
//                },
//                bodyFont: {
//                    size: 24
//                }
//            }
//        },
//        scales: {
//            x: {
//                beginAtZero: true,
//                stacked: true,
//                type: 'linear',
//                min: 0.0,
//                max: 1.0,
//                offset: false,
//                title: {
//                    display: true,
//                    text: 'Read similarity to contaminated database ',
//                    font: {
//                        size: 24
//                    }
//                }
//            },
//            y: {
//                stacked: true,
//                type: 'logarithmic',
//                title: {
//                    display: true,
//                    text: 'Number of reads (log-scale)',
//                    font: {
//                        size: 24
//                    }
//                }
//            }
//        }
//    };
//
//    chart.update()
//}
//
//const draw_species_list = () => {
//    const species_list_container = document.getElementById("species_list");
//    const threshold_list = df.index.filter(item => item >= k_mer_threshold);
//
//    let sum_classified_df = df.loc({ rows: threshold_list}).sum({axis: 0});
//
//    const sorted_series_by_freq = get_sorted_species_df(sum_classified_df);
//        
//    let zipped = _.zip(sorted_series_by_freq.index, sorted_series_by_freq.values)
//    zipped = zipped.filter(val => val[1] != 0)
//    const all_species = zipped.map((val) => {
//        let toggle = document.createElement("label");
//        toggle.classList = ["flex flex-row justify-between"]
//        toggle.setAttribute("id", "toggle_" + val[0]);
//        const checkbox = document.createElement("div");
//
//        const input = document.createElement("input");
//        input.setAttribute("type", "checkbox");
//        input.setAttribute("id", val[0]);
//        input.setAttribute("class", "h-5 w-5  accent-amber-500")
//        input.checked = species_list.includes(val[0]) ? true : false;
//
//        input.addEventListener("click", (change) => {
//            const item = change.target;
//            unchecked_all = false;
//            checked_all = false;
//            update_species_list(item);
//            //update the species_list to sent to backend
//            draw_kmer_hist(bar_chart, pie_chart);
//            draw_species_pie_chart(pie_chart);
//        });
//        
//        let label = document.createElement("span");
//        label.innerText = val[0];
//        checkbox.appendChild(input)
//        checkbox.appendChild(label);
//        toggle.appendChild(checkbox);
//
//        const num_reads = document.createElement("span");
//        num_reads.setAttribute("id", "numreads_" + val[0]);
//        num_reads.classList = ["px-4"]
//        num_reads.innerText = val[1];
//        toggle.appendChild(num_reads);
//        return toggle;
//    });
//
//    species_list_container.replaceChildren(...all_species)
//
//}
//
//
//
//// sorted species list by reads without unclassified entry
//const get_sorted_species_df = (df_to_sort) => {
//    let sort_index = df_to_sort.sortValues({"ascending": false }).index
//    let sorted_index_by_freq = df_to_sort.loc(sort_index).index
//
//    sorted_index_by_freq = sorted_index_by_freq.filter(item => item != non_contaminant_col_name)
//    return df_to_sort.loc(sorted_index_by_freq);
//}
//
//
//const confirm_export = (e) => {
//    if(!is_changed){
//        if(!confirm(HELP_TEXT_CONFIRM_EXPORT_NO_CHANGE.trim())) {
//            e.preventDefault();
//        }
//    }
//}
//
//document.getElementById("help_text_bar_similarites").innerText = HELP_TEXT_BAR_SIMILARITES.trim()
//document.getElementById("help_text_species_list").innerText = HELP_TEXT_SPECIES_LIST.trim()
//document.getElementById("help_text_pie_chart").innerText = HELP_TEXT_PIE_CHART.trim()
//
//
////download pie chart
//document.getElementById("download_pie").addEventListener('click', function(){
//    /*Get image of canvas element*/
//    var url_base64jp = document.getElementById("pie_chart").toDataURL("image/jpg");
//    /*get download button (tag: <a></a>) */
//    var a =  document.getElementById("download_pie");
//    /*insert chart image url to download button (tag: <a></a>) */
//    a.href = url_base64jp;
//});
//
////download histogram chart
//document.getElementById("download_histogram").addEventListener('click', function(){
//    /*Get image of canvas element*/
//    var url_base64jp = document.getElementById("bar_chart").toDataURL("image/jpg");
//    /*get download button (tag: <a></a>) */
//    var a =  document.getElementById("download_histogram");
//    /*insert chart image url to download button (tag: <a></a>) */
//    a.href = url_base64jp;
//});
//
//
//const set_selection = (flag) => {
//    const species_checkbox_list = [...document.getElementById("species_list").getElementsByTagName('input')];
//    
//    species_checkbox_list.forEach(item => {
//        item.checked = flag;
//        update_species_list(item);
//    });
//    unchecked_all = !flag;
//    checked_all = flag;
//
//    draw_kmer_hist(bar_chart, pie_chart);
//    draw_species_pie_chart(pie_chart);
//}
//
//document.getElementById("select_button").addEventListener("click",() => set_selection(true))
//document.getElementById("unselect_button").addEventListener("click",() => set_selection(false))
//
//document.getElementById("download_matrix").addEventListener("click", () => {
//    df.toCSV({ fileName: "matrix.csv", download: true})
//});


// all code below from: https://gist.github.com/mitchac/7aa120d1ef89b737d1f3fcee8698fbdd

// parse Newick format phylogeny source file
// adapted from https://github.com/jasondavies/newick.js and https://gist.github.com/git-ashish/3aa81521f96e48198c80b4e2742bb6bc
function parseNewick(a){for(var e=[],r={},s=a.split(/\s*(;|\(|\)|,|:)\s*/),t=0;t<s.length;t++){var n=s[t];switch(n){case"(":var c={};r.branchset=[c],e.push(r),r=c;break;case",":var c={};e[e.length-1].branchset.push(c),r=c;break;case")":r=e.pop();break;case":":break;default:var h=s[t-1];")"==h||"("==h||","==h?r.name=n:":"==h&&(r.length=parseFloat(n))}}return r}

// import source file
// url for original source file is..
// https://gist.githubusercontent.com/mbostock/c034d66572fd6bd6815a/raw/98778537e42f5605d9eddae5fba3329d969b813c/life.txt

// here importing local copy with slight modifications. 

let innerRadius = 307
let width = 954
let outerRadius = 477

let color = d3.scaleOrdinal()
    .domain(["Bacteria", "Eukaryota", "Archaea"])
    .range(d3.schemeCategory10)

let legend = svg => {
    const g = svg
        .selectAll("g")
        .data(color.domain())
        //.join("g")
        //    .attr("transform", (d, i) => `translate(${-outerRadius},${-outerRadius + i * 20})`);

    g.append("rect")
        .attr("width", 18)
        .attr("height", 18)
        .attr("fill", color);

    g.append("text")
        .attr("x", 24)
        .attr("y", 9)
        .attr("dy", "0.35em")
        .text(d => d);
}

function linkStep(startAngle, startRadius, endAngle, endRadius) {
    const c0 = Math.cos(startAngle = (startAngle - 90) / 180 * Math.PI);
    const s0 = Math.sin(startAngle);
    const c1 = Math.cos(endAngle = (endAngle - 90) / 180 * Math.PI);
    const s1 = Math.sin(endAngle);
    return "M" + startRadius * c0 + "," + startRadius * s0
        + (endAngle === startAngle ? "" : "A" + startRadius + "," + startRadius + " 0 0 " + (endAngle > startAngle ? 1 : 0) + " " + startRadius * c1 + "," + startRadius * s1)
        + "L" + endRadius * c1 + "," + endRadius * s1;
}


// Compute the maximum cumulative length of any node in the tree.
function maxLength(d) {
    return d.data.length + (d.children ? d3.max(d.children, maxLength) : 0);
}

// Set the radius of each node by recursively summing and scaling the distance from the root.
function setRadius(d, y0, k) {
    d.radius = (y0 += d.data.length) * k;
    if (d.children) d.children.forEach(d => setRadius(d, y0, k));
}

// Set the color of each node by recursively inheriting.
function setColor(d) {
    var name = d.data.name;
    d.color = color.domain().indexOf(name) >= 0 ? color(name) : d.parent ? d.parent.color : null;
    //d.color = colors[2]
    if (d.children) d.children.forEach(setColor);
}

function linkExtensionConstant(d) {
  return linkStep(d.target.x, d.target.y, d.target.x, innerRadius);
}

function linkExtensionVariable(d) {
  return linkStep(d.target.x, d.target.radius, d.target.x, innerRadius);
}

function linkConstant(d) {
  return linkStep(d.source.x, d.source.y, d.target.x, d.target.y);
}

function linkVariable(d) {
  return linkStep(d.source.x, d.source.radius, d.target.x, d.target.radius);
}


function createChart () {
    
    const root = d3.hierarchy(parseNewick("(B:0.2,(C:0.3,D:0.4):0.5);"), function (d) {
        return d.branchset;
        })
        .sum(function (d) {
            return d.branchset ? 0 : 1;
        })
        .sort(function (a, b) {
            return (a.value - b.value) || d3.ascending(a.data.length, b.data.length);
        });

    d3.cluster(root);
    setRadius(root, root.data.length = 0, innerRadius / maxLength(root));
    setColor(root);

    const svg = d3.create("svg")
        .attr("viewBox", [-outerRadius, -outerRadius, width, width])
        .attr("font-family", "sans-serif")
        .attr("font-size", 10);

    svg.append("g")
        .call(legend);

    svg.append("style").text(`

      .link--active {
          stroke: #000 !important;
          stroke-width: 1.5px;
      }

      .link-extension--active {
          stroke-opacity: .6;
      }

      .label--active {
          font-weight: bold;
      }

      `);

    const linkExtension = svg.append("g")
        .attr("fill", "none")
        .attr("stroke", "#000")
        .attr("stroke-opacity", 0.25)
        .selectAll("path")
        .data(root.links().filter(d => !d.target.children))
        //.join("path")
        .each(function(d) { d.target.linkExtensionNode = this; })
        .attr("d", linkExtensionConstant);

    const link = svg.append("g")
        .attr("fill", "none")
        .attr("stroke", "#000")
        .selectAll("path")
        .data(root.links())
        //.join("path")
        .each(function(d) { d.target.linkNode = this; })
        .attr("d", linkConstant)
        .attr("stroke", d => d.target.color);

    svg.append("g")
        .selectAll("text")
        .data(root.leaves())
        //.join("text")
            .attr("dy", ".31em")
            .attr("transform", d => `rotate(${d.x - 90}) translate(${innerRadius + 4},0)${d.x < 180 ? "" : " rotate(180)"}`)
            .attr("text-anchor", d => d.x < 180 ? "start" : "end")
            .text(d => d.data.name.replace(/_/g, " "))
            .on("mouseover", mouseovered(true))
            .on("mouseout", mouseovered(false));

    function update(checked) {
        const t = d3.transition().duration(750);
        linkExtension.transition(t).attr("d", checked ? linkExtensionVariable : linkExtensionConstant);
        link.transition(t).attr("d", checked ? linkVariable : linkConstant);
    }

    function mouseovered(active) {
        return function(event, d) {
            d3.select(this).classed("label--active", active);
            d3.select(d.linkExtensionNode).classed("link-extension--active", active).raise();
            do d3.select(d.linkNode).classed("link--active", active).raise();
            while (d = d.parent);
        };
    }
    
    return Object.assign(svg.node(), {update});
}

chart = createChart()
update = chart.update(true)

cluster = d3.cluster()
    .size([360, innerRadius])
    .separation((a, b) => 1)


color = d3.scaleOrdinal()
    .domain(["Bacteria", "Eukaryota", "Archaea"])
    .range(d3.schemeCategory10)


//d3.text("tree-of-life.txt", function (error, life) {
//    if (error) throw error;
//    
//    // parse imported data and convert to d3 hierarchy 
//    var root = d3.hierarchy(parseNewick("(B:0.2,(C:0.3,D:0.4):0.5);"), function (d) {
//            return d.branchset;
//        })
//        .sum(function (d) {
//            return d.branchset ? 0 : 1;
//        })
//        .sort(function (a, b) {
//            return (a.value - b.value) || d3.ascending(a.data.length, b.data.length);
//        });
//    
//    // color descendent nodes of each of three main domains of life. Ie Bacteria, Eukarya and Archaea. 
//    function colorEntireChilderen(node, color) {
//        node.color = color
//        if(!node.children) {
//            return;
//        }
//        node.children.forEach(function(d) {
//            console.log(d)
//            colorEntireChilderen(d, color);
//        }) 
//        return;
//    }
//
//    colorEntireChilderen(root.children[0], "#ff3333")
//    colorEntireChilderen(root.children[1], "#0092cc")
//    
//    //root.children[1].each(function (d) {
//    //    d.color = "#0092cc";
//    //});
//    
//    
//    // convert d3 hierarchy data structure to list of links and list of nodes
//    var links = [];
//    var nodes = [];
//    
//    // func for adding only unique objects to array 
//    function addUnique(object, array) {
//        if (object) {
//            if (array.filter(x => x.id === object.id).length === 0) {
//                array.push(object)
//            }
//        }
//    }
//    
//    // add only unique nodes to node list from link list 
//    root.links().forEach(function (value) {
//        var source = value.source.data.name;
//        var sourceColor = (value.source.color ? value.source.color : "#9e9e9e");
//        var sourceHeight = value.source.height;
//        
//        var target = value.target.data.name;
//        var targetColor = value.target.color;
//        var targetHeight = value.target.height;
//        
//        var length = value.target.data.length;
//        
//        links.push({
//            source: source,
//            target: target,
//            length: length,
//            color: sourceColor
//        });
//        
//        // add only unique nodes to node list from link list 
//        addUnique({
//            id: source,
//            color: sourceColor,
//            height: sourceHeight
//        }, nodes);
//        
//        addUnique({
//            id: target,
//            color: targetColor,
//            height: targetHeight
//        }, nodes);
//    
//    });
//    
//    // combine node and link info 
//    const gData = {
//        nodes: nodes,
//        links: links
//    };
//    
//    console.log(gData);
//    
//    // create graph and set attributes
//    const Graph = ForceGraph3D()
//        (document.getElementById('3d-graph'))
//        .graphData(gData)
//        .nodeThreeObject((d) => {
//            return new THREE.Mesh(
//                new THREE.SphereGeometry((d.height/2)+3),
//                new THREE.MeshLambertMaterial({
//                    color: d.color,
//                    //wireframe: true,
//                    opacity: 1
//                }))
//        })
//        .nodeLabel(d =>
//            `<span style="color: #505050; background-color: #FFFFFF">${d.id.replace(/\d+/g, '').replace(/_/g, ' ')}</span>`
//        )
//        //.nodeColor(node => node.color)
//        //.linkColor(link => link.color)
//        .linkOpacity(0.5)
//        .linkWidth(3)
//        //.nodeRelSize(6.5)
//        .warmupTicks(600)
//        .cooldownTicks(200)
//        .cameraPosition({
//            "x": -875.5037383561942,
//            "y": 1442.0922937307018,
//            "z": 427.8755760856578,
//        }, {
//            "x": -378.9171700100701,
//            "y": 606.9388718746914,
//            "z": 191.40032981151415
//        })
//        .onNodeClick(node => {
//            // Aim at node from outside it
//            const distance = 850;
//            const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);
//        
//            Graph.cameraPosition({
//                    x: node.x * distRatio,
//                    y: node.y * distRatio,
//                    z: node.z * distRatio
//                }, // new position
//                node, // lookAt ({ x, y, z })
//                3000 // ms transition duration
//            );
//        });
//    
//    // set forces on graph 
//    const linkForce = Graph
//        .d3AlphaDecay(0.015)
//        .d3VelocityDecay(0.015)
//        .d3Force('link')
//        .distance(link => link.length * 800)
//        .iterations(50)
//        .strength(1)
//});