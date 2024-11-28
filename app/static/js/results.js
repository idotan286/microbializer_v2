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


let max_num_of_rows = 0;
let table_offset = 0;
let LIMIT = 10
let orthologous_data_columns = {}

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
    var div = document.createElement("div")
    var label = document.createElement("label")
    var radio = document.createElement("input")
    radio.type = "radio"
    radio.name = group
    radio.id = text
    radio.classList = "hidden peer"
    label.classList = "text-center h-fit text-xs flex flex-row  bg-white peer-checked:bg-lime-600 peer-checked:text-white  rounded-md  shadow-lg  tracking-wide  uppercase  border border-lime-800  hover:bg-lime-600 hover:text-white font-bold  ease-linear  transition-all   mx-2  my-4 px-2  py-3  cursor-pointer"
    label.setAttribute("for", text);
    //radio.group = group
    if (is_default) {
        radio.checked = "checked"
        updateBarPlot(genomes_data, index)
    }
    div.classList = "my-2"
    div.appendChild(radio)

    label.appendChild(document.createTextNode(text))
    label.addEventListener("click", (change) => {
        updateBarPlot(genomes_data, index)
    });
    div.appendChild(label)
    return div;
}


const parseNewick = (a) => {for(var e=[],r={},s=a.split(/\s*(;|\(|\)|,|:)\s*/),t=0;t<s.length;t++){var n=s[t];switch(n){case"(":var c={};r.branchset=[c],e.push(r),r=c;break;case",":var c={};e[e.length-1].branchset.push(c),r=c;break;case")":r=e.pop();break;case":":break;default:var h=s[t-1];")"==h||"("==h||","==h?r.name=n:":"==h&&(r.length=parseFloat(n))}}return r}


const initResultsScript = (histogram_data, max_num_of_rows_inp, tree_str) => {
    const json_histogram_data = JSON.parse(histogram_data);
    max_num_of_rows = max_num_of_rows_inp;
    console.log(max_num_of_rows)
    const json_tree_str = JSON.parse(tree_str);
    runResultsScript(json_histogram_data, max_num_of_rows, json_tree_str)
};


const addAlpha = (color) => {
    // coerce values so ti is between 0 and 1.
    const _opacity = Math.round(Math.min(Math.max(0.1 || 1, 0), 1) * 255);
    return color + _opacity.toString(16).toUpperCase();
}

const runResultsScript = async (histogram_data, max_num_of_rows, tree_str) => {
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
    if (tree_data != "" && Object.keys(tree_data || {}).length > 0) {
        const treeChart = createChart(tree_data)
        let container = document.getElementById("phylo_tree_container")
        container.append(treeChart);
    }

    // create rightmost panel (OG table)
    const orthologous_data = await get_table_data(0, LIMIT);
    orthologous_data_columns = orthologous_data.columns


    createTable(0);

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


const createTable = async (offset) => {
  var table = document.getElementById('ortologic_table');
  table.innerHTML = '';
  var headers_tr = document.createElement('tr');
  // headers_tr.classList = "flex flex-row"
  var th = document.createElement('th');
  var text = document.createTextNode('');
  th.style.cssText = 'position:sticky; top:0; writing-mode:vertical-rl; background-color:white; z-index: 99;'; // = 'rotate(90.0deg)'
  th.appendChild(text)
  headers_tr.appendChild(th)


  const orthologous_data = await get_table_data(offset, LIMIT);
  if (orthologous_data_columns.length < 8){
    table.classList += "w-full";
  } else{
    let width = orthologous_data_columns.length * 64 + 20;
    table.style.cssText += "width:" + width + "px";
  }

  Object.values(orthologous_data_columns).forEach((key, index) => {
      console.log(key, index)
      var th = document.createElement('th');
      var text = document.createTextNode(key);
      th.style.cssText = 'position:sticky; top:0; writing-mode:vertical-rl; background-color:white; z-index: 99; width: 48px'
      th.appendChild(text)
      headers_tr.appendChild(th)
  });
  table.appendChild(headers_tr);
  
  Object.values(orthologous_data.index).forEach((key, index) => {
      var tr = document.createElement('tr');
      var th = document.createElement('th');
      th.classList = "border-4 border-gray-200"
      // tr.classList = "flex flex-row "
      // th.style.position = 'sticky';
      // th.style.left = '0';
      var text = document.createTextNode(key);
      th.appendChild(text)
      tr.appendChild(th)
      Object.values(orthologous_data.data[index]).forEach((key, index) => {
          var td = document.createElement('td');
          td.style.cssText = 'text-align:center;'
          if (key === 0){
            td.classList = "bg-rose-600"
              // td.style.cssText += 'background-color:red;'
          } else if (key === 1){
            td.classList = "bg-emerald-600"

          }
          tr.appendChild(td);
      })
      table.appendChild(tr);
  })
}

const get_table_data = (offset, limit) => {
  const url = new URL(window.location.href);
  const resultId = url.pathname.replace('/results/', '');
  const xhr = new XMLHttpRequest();

  return new Promise((resolve, reject) => {
      xhr.open("GET", `/get_table/${resultId}?offset=${offset}&limit=${limit}`, true);

      xhr.onreadystatechange = () => {
          if (xhr.readyState === 4) {
              if (xhr.status >= 200 && xhr.status < 300) {
                  resolve(JSON.parse(xhr.responseText));
              } else {
                  reject(`Error: ${xhr.status}`);
              }
          }
      };

      xhr.send();
  });
};
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
      .attr("id", "tree")
      .attr("viewBox", [-outerRadius, -outerRadius, width, width])
      .attr("font-family", "sans-serif")
      .attr("font-size", 16);

  //svg.append("g")
  //    .call(legend);

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

document.getElementById("table_down").addEventListener("click", () => {
  new_offset = table_offset + LIMIT
  if (new_offset > max_num_of_rows) {
    new_offset = max_num_of_rows
  }

  createTable(new_offset)
  table_offset = new_offset
})

document.getElementById("table_up").addEventListener("click", () => {
  new_offset = table_offset - LIMIT
  if (new_offset < 0) {
    new_offset = 0
  }

  createTable(new_offset)
  table_offset = new_offset
})

document.getElementById("download_page").addEventListener("click", () => {
  const resultId = url.pathname.replace('/results/', '');
  document.location.href = `/download_page/${resultId}`;
})

document.getElementById("download_all").addEventListener("click", () => {
  let request = new XMLHttpRequest();
  request.open('POST', '');
  var data = JSON.stringify({"action": "download_all"});
  request.send(data);
})