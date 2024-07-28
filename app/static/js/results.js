// Permission to use, copy, modify, and/or distribute this software for any
// purpose with or without fee is hereby granted, provided that the above
// copyright notice and this permission notice appear in all copies.

// THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
// WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
// MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
// ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
// WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
// ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
// OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


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
          display: false
      },
      title: {
          display: false
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


const parseNewick = (a) => {for(var e=[],r={},s=a.split(/\s*(;|\(|\)|,|:)\s*/),t=0;t<s.length;t++){var n=s[t];switch(n){case"(":var c={};r.branchset=[c],e.push(r),r=c;break;case",":var c={};e[e.length-1].branchset.push(c),r=c;break;case")":r=e.pop();break;case":":break;default:var h=s[t-1];")"==h||"("==h||","==h?r.name=n:":"==h&&(r.length=parseFloat(n))}}return r}



const initResultsScript = (histogram_data, orthologous_data, tree_str) => {
    const json_histogram_data = JSON.parse(histogram_data);
    const json_orthologous_data = JSON.parse(orthologous_data);
    console.log(tree_str)
    const json_tree_str = JSON.parse(tree_str);
    runResultsScript(json_histogram_data, json_orthologous_data, json_tree_str)
};


const addAlpha = (color) => {
    // coerce values so ti is between 0 and 1.
    const _opacity = Math.round(Math.min(Math.max(0.1 || 1, 0), 1) * 255);
    return color + _opacity.toString(16).toUpperCase();
}

const runResultsScript = (histogram_data, orthologous_data, tree_str) => {
    console.log('inside runResultsScript') 
    // create leftmost panel (histogram)
    const radio_bar_plot_parameters = document.getElementById("parameters_option_bar_chart")
    Object.keys(histogram_data).forEach((key, index) => {
        var radio_btn = makeRadioButton("bar_plot_options", " " + key, index === 0, histogram_data[key], index)
        radio_bar_plot_parameters.appendChild(radio_btn)
    });
    //console.log(orthologous_data)
    
    // middle panel (phylo tree )
    const tree_data = parseNewick(tree_str);
    //console.log(tree_data)
    // only if tree data is have items
    if (tree_data != "") {
        const treeChart = createChart(tree_data)
        let container = document.getElementById("phylo_tree_container")
        container.append(treeChart);
    }

    // create rightmost panel (OG table)
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


// all code below from: https://gist.github.com/mitchac/7aa120d1ef89b737d1f3fcee8698fbdd

// parse Newick format phylogeny source file
// adapted from https://github.com/jasondavies/newick.js and https://gist.github.com/git-ashish/3aa81521f96e48198c80b4e2742bb6bc



let width = 954
let outerRadius = width / 2

let innerRadius = outerRadius - 170

let cluster = d3.cluster()
    .size([360, innerRadius])
    .separation((a, b) => 1)

let color = d3.scaleOrdinal()
    .domain(["Bacteria", "Eukaryota", "Archaea"])
    .range(d3.schemeCategory10)


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
  if (d.children) d.children.forEach(setColor);
}

function linkVariable(d) {
  return linkStep(d.source.x, d.source.radius, d.target.x, d.target.radius);
}

function linkConstant(d) {
  return linkStep(d.source.x, d.source.y, d.target.x, d.target.y);
}

function linkExtensionVariable(d) {
  return linkStep(d.target.x, d.target.radius, d.target.x, innerRadius);
}

function linkExtensionConstant(d) {
  return linkStep(d.target.x, d.target.y, d.target.x, innerRadius);
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

let legend = svg => {
  const g = svg
    .selectAll("g")
    .data(color.domain())
    .join("g")
      .attr("transform", (d, i) => `translate(${-outerRadius},${-outerRadius + i * 20})`);

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




let createChart = (data) => {
  const root = d3.hierarchy(data, d => d.branchset)
      .sum(d => d.branchset ? 0 : 1)
      .sort((a, b) => (a.value - b.value) || d3.ascending(a.data.length, b.data.length));

  cluster(root);
  setRadius(root, root.data.length = 0, innerRadius / maxLength(root));
  //setColor(root);

  const svg = d3.create("svg")
      .attr("viewBox", [-outerRadius, -outerRadius, width, width])
      .attr("font-family", "sans-serif")
      .attr("font-size", 16);

  svg.append("g")
      .call(legend);

  svg.append("style").text(`

.link--active {
  stroke: #000 !important;
  stroke-width: 3px;
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
      .attr("stroke-opacity", 0.5)
    .selectAll("path")
    .data(root.links().filter(d => !d.target.children))
    .join("path")
      .each(function(d) { d.target.linkExtensionNode = this; })
      .attr("d", linkExtensionConstant);

  const link = svg.append("g")
      .attr("fill", "none")
      .attr("stroke", "#000")
    .selectAll("path")
    .data(root.links())
    .join("path")
      .each(function(d) { d.target.linkNode = this; })
      .attr("d", linkConstant)
      .attr("stroke", d => d.target.color);

  svg.append("g")
    .selectAll("text")
    .data(root.leaves())
    .join("text")
      .attr("dy", ".31em")
      .attr("transform", d => `rotate(${d.x - 90}) translate(${innerRadius + 4},0)${d.x < 180 ? "" : " rotate(180)"}`)
      .attr("text-anchor", d => d.x < 180 ? "start" : "end")
      .text(d => d.data.name.replace(/_/g, " "))
      .on("mouseover", mouseovered(true))
      .on("mouseout", mouseovered(false));

  function update(checked) {
    // const t = d3.transition().duration(750);
    // linkExtension.transition(t).attr("d", checked ? linkExtensionVariable : linkExtensionConstant);
    // link.transition(t).attr("d", checked ? linkVariable : linkConstant);
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
};
