$(function(){
	// Initiate graphs right after interface loaded
	rungraphs();

});

function rungraphs(){
	var seriesData = [ [], [], []];
var random = new Rickshaw.Fixtures.RandomData(1540000);

for (var i = 0; i < 200; i++) {
	random.addData(seriesData);
}

var graph = new Rickshaw.Graph( {
	element: document.querySelector("#chart-2"),
	width: $("#chart-2").parent().width(),
  renderer: 'area',
  series: [
    {
      color: "#0083c1",
      data: seriesData[0],
      name: 'Photodune'
    }, 
	
	{
      color: "#81c5e5",
      data: seriesData[1],
      name: 'Codecanyon'
    }, 
	
	{
      color: "#dbf1fe",
      data: seriesData[2],
      name: 'Themeforest'
    }
  ]
} );

graph.render();
var hoverDetail = new Rickshaw.Graph.HoverDetail( {
  graph: graph,
  formatter: function(series, x, y) {
    var date = '<span class="date">' + new Date(x * 1000).toUTCString() + '</span>';
    var swatch = '<span class="detail_swatch" style="background-color: ' + series.color + '"></span>';
    var content = swatch + series.name + ": " + parseInt(y) + '<br>' + date;
    return content;
  }
} );


	var graph = new Rickshaw.Graph({
		element: document.querySelector("#chart-1"),
		width: $("#chart-1").parent().width(),
		height: 235,
		renderer: 'line',
		series: [{
			data: [ { x: 0, y: 40 }, { x: 1, y: 49 }, { x: 2, y: 38 }, { x: 3, y: 30 }, { x: 4, y: 32 } ],
			color: '#0083c1'
		}, {
			data: [ { x: 0, y: 20 }, { x: 1, y: 24 }, { x: 2, y: 19 }, { x: 3, y: 15 }, { x: 4, y: 16 } ],
			color: '#5b5b5b'
		}]
	});
	graph.render();

	var graph = new Rickshaw.Graph( {
		element: document.querySelector("#chart-3"),
		height: 235,
		renderer: 'bar',
		stack: false,
		series: [ 
			{
				data: [ { x: 0, y: 40 }, { x: 1, y: 49 }, { x: 2, y: 38 }, { x: 3, y: 30 }, { x: 4, y: 32 } ],
				color: '#0083c1'
			}, {
				data: [ { x: 0, y: 20 }, { x: 1, y: 24 }, { x: 2, y: 19 }, { x: 3, y: 15 }, { x: 4, y: 16 } ],
				color: '#81c5e5'

		} ]
	} );

	graph.render();

	var graph = new Rickshaw.Graph( {
	        element: document.querySelector("#chart-4"),
	        renderer: 'bar',
	        height: 235,
	        stack: true,
	        	series: [ 
		{
			data: [ { x: 0, y: 40 }, { x: 1, y: 49 }, { x: 2, y: 38 }, { x: 3, y: 30 }, { x: 4, y: 32 } ],
			color: '#0083c1'
		}, {
			data: [ { x: 0, y: 20 }, { x: 1, y: 24 }, { x: 2, y: 19 }, { x: 3, y: 15 }, { x: 4, y: 16 } ],
			color: '#81c5e5'

	} ]
} );

graph.render();
// set up our data series with 50 random data points

var seriesData = [ [], [], [] ];
var random = new Rickshaw.Fixtures.RandomData(150);

for (var i = 0; i < 150; i++) {
	random.addData(seriesData);
}

// instantiate our graph!

var graph = new Rickshaw.Graph( {
	element: document.getElementById("chart-5"),
	height: 500,
	renderer: 'line',
	series: [
		{
			color: "#6FB07F",
			data: seriesData[0],
			name: 'New York'
		}, {
			color: "#FCB03C",
			data: seriesData[1],
			name: 'London'
		}, {
			color: "#FC5B3F",
			data: seriesData[2],
			name: 'Tokyo'
		}
	]
} );

graph.render();

var hoverDetail = new Rickshaw.Graph.HoverDetail( {
	graph: graph
} );

var legend = new Rickshaw.Graph.Legend( {
	graph: graph,
	element: document.getElementById('legend')

} );

var shelving = new Rickshaw.Graph.Behavior.Series.Toggle( {
	graph: graph,
	legend: legend
} );

var axes = new Rickshaw.Graph.Axis.Time( {
	graph: graph
} );
axes.render();	
}