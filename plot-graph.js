var nodes = null;
var edges = null;
var network = null;

function draw() {
  nodes = new vis.DataSet(dataset_nodes);
  edges = new vis.DataSet(dataset_edges);

  // Instantiate our network object.
  var container = document.getElementById('mynetwork');
  var data = {
    nodes: nodes,
    edges: edges
  };
  var options = {
    layout: {
      randomSeed : 10000,
    },    
    nodes: {
      shape: 'dot',
      scaling: {
        customScalingFunction: function (min,max,total,value) {
          return value/total;
        },
        min: 10,
        max: 100
      }
    }
  };
  var network = new vis.Network(container, data, options);
  network.on("click", function (params) {
    if (nodes.get(params.nodes[0]).info) {
      document.getElementById('info').innerHTML = '<h2>Description:</h2>' + nodes.get(params.nodes[0]).info;
    } else {
      document.getElementById('info').innerHTML = '';
    }
  });
}
