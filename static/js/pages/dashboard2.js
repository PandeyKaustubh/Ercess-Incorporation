//[Dashboard Javascript]

//Project:	SoftPro admin - Responsive Admin Template
//Primary use:   Used only for the main dashboard (index.html)

$(function () {

  'use strict';
	
	
	let draw = Chart.controllers.line.prototype.draw;
    Chart.controllers.line = Chart.controllers.line.extend({
        draw: function() {
            draw.apply(this, arguments);
            let ctx = this.chart.chart.ctx;
            let _stroke = ctx.stroke;
            ctx.stroke = function() {
                ctx.save();
                ctx.shadowColor = '#888';
                ctx.shadowBlur = 20;
                ctx.shadowOffsetX = 0;
                ctx.shadowOffsetY = 1;
                _stroke.apply(this, arguments)
                ctx.restore();
            }
        }
    });

    var ctx = document.getElementById("canvas1");
    // ctx.height = 200;
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "Mon"],
            datasets: [{
                data: [100, 70, 150, 120, 300, 250, 400, 300],
                borderWidth: 3,
                borderColor: "#0bb2d4",
                pointBackgroundColor: "#FFF",
                pointBorderColor: "#0bb2d4",
                pointHoverBackgroundColor: "#FFF",
                pointHoverBorderColor: "#0bb2d4",
                pointRadius: 0,
                pointHoverRadius: 6,
                fill: !1
            }]
        },
        options: {
            responsive: !0,
            maintainAspectRatio: false, 
            legend: {
                display: !1
            },
            scales: {
                xAxes: [{
                    display: !1,
                    gridLines: {
                        display: !1
                    }
                }],
                yAxes: [{
                    display: !1,
                    ticks: {
                        padding: 10,
                        stepSize: 100,
                        max: 600,
                        min: 0
                    },
                    gridLines: {
                        display: !0,
                        draw1Border: !1,
                        lineWidth: 0.5,
                        zeroLineColor: "#e5e5e5"
                    }
                }]
            }
        },
    });



    var ctx = document.getElementById("canvas2");
    // ctx.height = 200;
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "Mon"],
            datasets: [{
                data: [100, 70, 150, 120, 300, 250, 400, 300],
                borderWidth: 3,
                borderColor: "#ff4c52",
                pointBackgroundColor: "#FFF",
                pointBorderColor: "#ff4c52",
                pointHoverBackgroundColor: "#FFF",
                pointHoverBorderColor: "#ff4c52",
                pointRadius: 0,
                pointHoverRadius: 6,
                fill: !1
            }]
        },
        options: {
            responsive: !0,
            maintainAspectRatio: false, 
            legend: {
                display: !1
            },
            scales: {
                xAxes: [{
                    display: !1,
                    gridLines: {
                        display: !1
                    }
                }],
                yAxes: [{
                    display: !1,
                    ticks: {
                        padding: 10,
                        stepSize: 100,
                        max: 600,
                        min: 0
                    },
                    gridLines: {
                        display: !0,
                        draw1Border: !1,
                        lineWidth: 0.5,
                        zeroLineColor: "#e5e5e5"
                    }
                }]
            }
        },
    });


    var ctx = document.getElementById("canvas3");
    // ctx.height = 200;
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "Mon"],
            datasets: [{
                data: [100, 70, 150, 120, 300, 250, 400, 300],
                borderWidth: 3,
                borderColor: "#faa700",
                pointBackgroundColor: "#FFF",
                pointBorderColor: "#faa700",
                pointHoverBackgroundColor: "#FFF",
                pointHoverBorderColor: "#faa700",
                pointRadius: 0,
                pointHoverRadius: 6,
                fill: !1
            }]
        },
        options: {
            responsive: !0,
            maintainAspectRatio: false, 
            legend: {
                display: !1
            },
            scales: {
                xAxes: [{
                    display: !1,
                    gridLines: {
                        display: !1
                    }
                }],
                yAxes: [{
                    display: !1,
                    ticks: {
                        padding: 10,
                        stepSize: 100,
                        max: 600,
                        min: 0
                    },
                    gridLines: {
                        display: !0,
                        draw1Border: !1,
                        lineWidth: 0.5,
                        zeroLineColor: "#e5e5e5"
                    }
                }]
            }
        },
    });

	 // [ Bar Chart2 ] Start
       var chart = AmCharts.makeChart("bar-chart2", {
           "type": "serial",
           "theme": "light",
           "marginTop": 10,
           "marginRight": 0,
           "valueAxes": [{
               "id": "v1",
               "position": "left",
               "axisAlpha": 0,
               "lineAlpha": 0,
               "autoGridCount": false,
               "labelFunction": function(value) {
                   return +Math.round(value) + "00";
               }
           }],
           "graphs": [{
               "id": "g1",
               "valueAxis": "v1",
               "lineColor": ["#04a9f5", "#14cc9e"],
               "fillColors": ["#04a9f5", "#14cc9e"],
               "fillAlphas": 1,
               "type": "column",
               "title": "SALES",
               "valueField": "sales",
               "columnWidth": 0.3,
               "legendValueText": "$[[value]]M",
               "balloonText": "[[title]]<br /><b style='font-size: 130%'>$[[value]]M</b>"
           },{
               "id": "g2",
               "valueAxis": "v1",
               "lineColor": ["#f44236", "#9C27B0"],
               "fillColors": ["#f44236", "#9C27B0"],
               "fillAlphas": 1,
               "type": "column",
               "title": "VISITS ",
               "valueField": "visits",
               "columnWidth": 0.3,
               "legendValueText": "$[[value]]M",
               "balloonText": "[[title]]<br /><b style='font-size: 130%'>$[[value]]M</b>"
           },{
               "id": "g3",
               "valueAxis": "v1",
               "lineColor": ["#E91E63", "#f4c22b"],
               "fillColors": ["#E91E63", "#f4c22b"],
               "fillAlphas": 1,
               "type": "column",
               "title": "CLICKS",
               "valueField": "clicks",
               "columnWidth": 0.3,
               "legendValueText": "$[[value]]M",
               "balloonText": "[[title]]<br /><b style='font-size: 130%'>$[[value]]M</b>"
           }],
           "chartCursor": {
               "pan": true,
               "valueLineEnabled": true,
               "valueLineBalloonEnabled": true,
               "cursorAlpha": 0,
               "valueLineAlpha": 0.2
           },
           "categoryField": "Year",
           "categoryAxis": {
               "dashLength": 1,
               "gridAlpha": 0,
               "axisAlpha": 0,
               "lineAlpha": 0,
               "minorGridEnabled": true
           },
           "legend": {
               "useGraphSettings": true,
               "position": "top"
           },
           "balloon": {
               "borderThickness": 1,
               "shadowAlpha": 0
           },
           "dataProvider": [{
               "Year": "2014",
               "sales": 2,
               "visits": 4,
               "clicks": 3
           },{
               "Year": "2015",
               "sales": 4,
               "visits": 7,
               "clicks": 5
           },{
               "Year": "2016",
               "sales": 2,
               "visits": 3,
               "clicks": 4
           },{
               "Year": "2017",
               "sales": 4.5,
               "visits": 6,
               "clicks": 4
           }]
       });
   // [ Bar Chart2 ] end


	
}); // End of use strict

