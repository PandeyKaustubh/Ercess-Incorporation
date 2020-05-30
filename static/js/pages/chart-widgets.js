//[custom Javascript]



// Fullscreen
$(function () {
	'use strict'
	// Composite line charts, the second using values supplied via javascript
    		
		$("#linechart").sparkline([32,24,26,24,32,26,40,34,22,24], {
			type: 'line',
			width: '100',
			height: '38',
			lineColor: '#14cc9e',
			fillColor: '#ffffff',
			lineWidth: 2,
			minSpotColor: '#14cc9e',
			maxSpotColor: '#14cc9e',
		});
		$("#linechart2").sparkline([32,24,26,24,32,26,40,34,22,24], {
			type: 'line',
			width: '100',
			height: '38',
			lineColor: '#3ebfea',
			fillColor: '#ffffff',
			lineWidth: 2,
			minSpotColor: '#3ebfea',
			maxSpotColor: '#3ebfea',
		});
		$("#linechart3").sparkline([32,24,26,24,32,26,40,34,22,24,22,24,34,32,38,28,36,36,40,38,30,34,38], {
			type: 'line',
			width: '100%',
			height: '45',
			lineColor: '#14cc9e',
			fillColor: '#ffffff',
			lineWidth: 2,
			minSpotColor: '#14cc9e',
			maxSpotColor: '#14cc9e',
		});
		$("#linechart4").sparkline([32,24,26,24,32,26,40,34,22,24], {
			type: 'line',
			width: '50%',
			height: '100',
			lineColor: '#14cc9e',
			fillColor: '#ffffff',
			lineWidth: 2,
			minSpotColor: '#14cc9e',
			maxSpotColor: '#14cc9e',
		});
	
		$("#barchart").sparkline([32,24,26,24,32,26,40,34,22,24], {
			type: 'bar',
			height: '38',
			width: '100%',
			barWidth: 6,
			barSpacing: 4,
			barColor: '#f4c22b',
		});
		$("#barchart2").sparkline([32,24,26,24,32,26,40,34,22,24], {
			type: 'bar',
			height: '38',
			barWidth: 6,
			barSpacing: 4,
			barColor: '#f4c22b',
		});
		$("#barchart3").sparkline([32,24,26,24,32,26,40,34,22,24,22,24,34,32,38,28,36,36,40,38,30,34,38], {
			type: 'bar',
			height: '45',
			width: '100%',
			barWidth: 6,
			barSpacing: 4,
			barColor: '#f44236',
		});
		$("#barchart4").sparkline([32,24,26,24,32,26,40,34,22,24], {
			type: 'bar',
			height: '100',
			width: '50%',
			barWidth: 6,
			barSpacing: 4,
			barColor: '#f44236',
		});
	
		$("#discretechart").sparkline([32,24,26,24,32,26,40,34,22,24], {
			type: 'discrete',
			width: '50',
			height: '38',
			lineColor: '#04a9f5',
		});
		$("#discretechart2").sparkline([32,24,26,24,32,26,40,34,22,24], {
			type: 'discrete',
			width: '50',
			height: '38',
			lineColor: '#04a9f5',
		});
		$("#discretechart3").sparkline([32,24,26,24,32,26,40,34,22,24,22,24,34,32,38,28,36,36,40,38,30,34,38], {
			type: 'discrete',
			width: '180',
			height: '45',
			lineColor: '#f4c22b',
		});
		$("#discretechart4").sparkline([32,24,26,24,32,26,40,34,22,24], {
			type: 'discrete',
			width: '100',
			height: '100',
			lineColor: '#f4c22b',
		});
		
		$("#linearea").sparkline([32,24,26,24,32,26,40,34,22,24], {
			type: 'line',
			width: '100%',
			height: '80',
			lineColor: '#14cc9e',
			fillColor: '#14cc9e',
			lineWidth: 2,
		});
		$("#linearea2").sparkline([32,24,26,24,32,26,40,34,22,24,22,24,34,32,38,28,36,36,40,38,30,34,38], {
			type: 'line',
			width: '100%',
			height: '45',
			lineColor: '#04a9f5',
			fillColor: '#04a9f5',
			lineWidth: 2,
		});
		$("#linearea3").sparkline([32,24,26,24,32,26,40,34,22,24], {
			type: 'line',
			width: '50%',
			height: '100',
			lineColor: '#04a9f5',
			fillColor: '#04a9f5',
			lineWidth: 1,
		});
		
		$("#baralc").sparkline([32,24,26,24,32,26,40,34,22,24,22,24,34,32,38,28,36,36,40,38,30,34,38], {
			type: 'bar',
			height: '80',
			barWidth: 6,
			barSpacing: 4,
			barColor: '#f4c22b',
		});
		
		$("#lineIncrease").sparkline([32,24,26,24,32,26,40,34,22,24], {
			type: 'line',
			width: '100%',
			height: '92',
			lineWidth: 2,
			lineColor: '#ffffff',
			fillColor: "#00BCD4",
			spotColor: '#ffffff',
			minSpotColor: '#ffffff',
			maxSpotColor: '#ffffff',
			spotRadius: 3,
		});
		
		$("#lineToday").sparkline([32,24,26,24,32,26,40,34,22,24], {
			type: 'line',
			width: '100%',
			height: '70',
			lineColor: '#ffffff',
			fillColor: '#9C27B0',
			lineWidth: 2,
			spotRadius: 3,
		});
		
		$("#baranl").sparkline([32,24,26,24,32,26,40,34,22,24,22,24,34,32,38,28,36,36,40,38,30,34,38], {
			type: 'bar',
			height: '70',
			barColor: '#f44236',
			barWidth: 7,
    		barSpacing: 5,
		});
		
		$("#lineTo").sparkline([32,24,26,24,32,26,40,34,22,24], {
			type: 'line',
			width: '100%',
			height: '70',
			lineColor: '#ffffff',
			fillColor: '#8d6658',
			lineWidth: 3,
			spotColor: '#ffffff',
			highlightSpotColor: '#ffffff',
			highlightLineColor: '#ffffff',
			spotRadius: 3,
		});
		
		// donut chart
		$('.donut').peity('donut');
		
		// bar chart
		$(".bar").peity("bar");	
	
		
		$('.countnm').each(function () {
			$(this).prop('Counter',0).animate({
				Counter: $(this).text()
			}, {
				duration: 1000,
				easing: 'swing',
				step: function (now) {
					$(this).text(Math.ceil(now));
				}
			});
		});
	
}); // End of use strict
		
// easypie chart
	$(function() {
		'use strict'
		$('.easypie').easyPieChart({
			easing: 'easeOutBounce',
			onStep: function(from, to, percent) {
				$(this.el).find('.percent').text(Math.round(percent));
			}
		});
		var chart = window.chart = $('.easypie').data('easyPieChart');
		$('.js_update').on('click', function() {
			chart.update(Math.random()*200-100);
		});
	});// End of use strict