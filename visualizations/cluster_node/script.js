Promise.all([
    d3.csv('../../nodes.csv'),
      d3.csv('../../edges.csv'),
      ]).then(makeChart)
      .catch(function(err) {
      console.log(err);
      })
    
    function makeChart(data) {
    data[0].forEach(function(d, i) {
        d.group = i
      });
      //
      data[0].forEach(function(d) { //nodes
        data[1].forEach(function(e) { //edges
    
          if (e.source === d.case_id || e.target === d.case_id) {
            data[0].find(function(f) {
              return f.case_id === e.source
            }).group = d.group;
            data[0].find(function(f) {
              return f.case_id === e.target
            }).group = d.group;
          }
    
        })
      
      });
    
    var winheight = window.innerHeight;
    var winwidth = window.innerWidth;
      var svg = d3.select("svg");
      svg.attr("viewBox", `0 0 ` + winwidth + ` ` + winheight +``);
    
      var force = d3.forceSimulation()
      .force("link", d3.forceLink()
        .id(function(d) {
          return d.case_id
        }))
      .force("charge", d3.forceManyBody().strength(-1))
      .force("collide", d3.forceCollide(22))
      .force("center", d3.forceCenter(winwidth/2, winheight/2));
    
      var div = d3.select("body").append("div")	
      .attr("class", "tooltip")				
      .style("opacity", 0);

    var edges = svg.selectAll("line")
      .data(data[1])
      .enter()
      .append("line")
      .style("stroke", "#aaa")
      .style("stroke-width", 2);
    
    var color = d3.scaleOrdinal(d3.schemeCategory10);
    
    var nodes = svg.selectAll("circle")
      .data(data[0])
      .enter()
      .append("circle")
      .attr("r", 16)
      .style("stroke", "#444")
      .style("stroke-width", 1)
      .style("fill", function(d) {
         if(d.case_id.includes("CLUSTER")) {
           return "black";
         }
        return color(d.group);
      })
      .on("mouseover", function(d) {		
        div.transition()		
            .duration(200)		
            .style("opacity", .9);		
        div	.html(d.case_id)	
            .style("left", (d3.event.pageX) + "px")	
            .style("cursor", "pointer")	
            .style("top", (d3.event.pageY - 28) + "px");	
        })					
    .on("mouseout", function(d) {		
        div.transition()		
            .duration(500)		
            .style("opacity", 0);	
    });
    
    //
    var labels = svg.selectAll("text")
      .data(data[0])
      .enter()
      .append("text")
      .attr('text-anchor', 'middle')
      .attr('class', 'textstyle')
      .style("fill", "white")
      .text(function(d) {return d.case_id });
    
    force.nodes(data[0]);
    force.force("link")
      .links(data[1]);
    
    force.on("tick", function() {
      edges.attr("x1", function(d) {
          return d.source.x;
        })
        .attr("y1", function(d) {
          return d.source.y;
        })
        .attr("x2", function(d) {
          return d.target.x;
        })
        .attr("y2", function(d) {
          return d.target.y;
        })
    
      nodes.attr("cx", function(d) {
          return d.x;
        })
        .attr("cy", function(d) {
          return d.y;
        });
    
        labels.attr("transform", function(d) {
          return "translate(" + d.x + "," + d.y + ")";
        });
    
    
    });
    
    } 
    
