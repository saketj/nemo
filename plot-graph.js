var nodes = null;
var edges = null;
var network = null;
var all_nodes = new vis.DataSet(dataset_nodes);
var all_edges = new vis.DataSet(dataset_edges);

var indegree_param = 0;
var outdegree_param = 1;
var excluded_nodes = {};
var included_categories = ['SSD', 'DISK', 'CPU', 'NETWORK', 'MEMORY'];

function draw() {
  $('#alertModal').modal('show');
  var indegrees = {};
  var outdegrees = {};

  // (1) Get edges which do not point to/originate from excluded nodes, & get indegrees/outdegrees.
  var edges = all_edges.get({
    filter: function(item) {
      var isIncluded = !(excluded_nodes.hasOwnProperty(item.from) || excluded_nodes.hasOwnProperty(item.to));
      if (isIncluded) {
          if (indegrees.hasOwnProperty(item.to)) {
            indegrees[item.to] = indegrees[item.to] + 1;
          } else {
            indegrees[item.to] = 1;
          }
          if (outdegrees.hasOwnProperty(item.from)) {
            outdegrees[item.from] = outdegrees[item.from] + 1;
          } else {
            outdegrees[item.from] = 1;
          }
      }
      return isIncluded;
    }
  });

  // (2) Remove nodes that do not satisfy the indegree and outdegrees
  var nodes = all_nodes.get({
    filter: function(item) {
      var isIncluded = true;

      // Check if category is included or not.
      if (included_categories.indexOf(item.category) < 0) {
        isIncluded = false;
      }

      if (indegrees.hasOwnProperty(item.id) || outdegrees.hasOwnProperty(item.id)) {
        // Check if desired indegree is available for this node.
        if (indegrees.hasOwnProperty(item.id) && indegrees[item.id] < indegree_param) {
          isIncluded = false;
        }
        // Check if desired outdegree is available for this node.
        if (outdegrees.hasOwnProperty(item.id) && outdegrees[item.id] < outdegree_param) {
          isIncluded = false;
        }
      } else {
        // this node is being removed because it has both indegree & outdegree zero.
        isIncluded = false;
      }

      if (!isIncluded) {
        excluded_nodes[item.id] = 1;
      }
      return isIncluded;
    }
  });

  // (3) Final edge removal based on excluded.
  edges = all_edges.get({
    filter: function(item) {
      return !(excluded_nodes.hasOwnProperty(item.from) || excluded_nodes.hasOwnProperty(item.to));
    }
  });


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
  network = new vis.Network(container, data, options);
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

  network.on("doubleClick", function (params) {
    excluded_nodes[params.nodes[0]] = 1;
    $('#alertModal').modal('show');
    draw();
  });
}

function applyFilter() {
  indegree_param = $('#indegree').val() ? parseInt($('#indegree').val()) : 0;
  outdegree_param = $('#outdegree').val() ? parseInt($('#outdegree').val()) : 1;
  included_categories = $("input[name='category']:checked").map(function(){
                            return $(this).val();
                          }).get();
  draw();
}

function applyReset() {
  indegree_param = 0;
  outdegree_param = 1;
  excluded_nodes = {};
  included_categories = ['SSD', 'DISK', 'CPU', 'NETWORK', 'MEMORY'];
  draw();
}
