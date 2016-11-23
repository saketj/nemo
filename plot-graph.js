var nodes = null;
var edges = null;
var network = null;
var all_nodes = null;
var edges = null;

var indegree_param = 0;
var outdegree_param = 0;
var included_nodes = {};
var included_categories = ['SSD', 'DISK', 'CPU', 'NETWORK', 'MEMORY']

function draw() {
  all_nodes = new vis.DataSet(dataset_nodes);
  all_edges = new vis.DataSet(dataset_edges);
  included_nodes = {};

  var nodes = all_nodes.get({
    filter: function(item) {
      if ((item.indegree >= indegree_param || item.outdegree >= outdegree_param)
            && (included_categories.indexOf(item.category)) >= 0){
        included_nodes[item.id] = 1;
        return 1 == 1;  // return true
      }
      return 1 != 1; // return false
    }
  });

  var edges = all_edges.get({
    filter: function(item) {
      return (included_nodes[item.from] && included_nodes[item.to]);
    }
  })

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
    if (all_nodes.get(params.nodes[0]).info) {
      document.getElementById('info').innerHTML = '<h2>Description:</h2>' + all_nodes.get(params.nodes[0]).info;
    } else {
      document.getElementById('info').innerHTML = '';
    }
  });

  network.on("afterDrawing", function() {
    $('#alertModal').modal('hide');
  });
}

function applyFilter() {
  indegree_param = $('#indegree').val() ? parseInt($('#indegree').val()) : 0;
  outdegree_param = $('#outdegree').val() ? parseInt($('#outdegree').val()) : 0;
  included_categories = $("input[name='category']:checked").map(function(){
                            return $(this).val();
                          }).get();
  $('#alertModal').modal('show');
  draw();
}
