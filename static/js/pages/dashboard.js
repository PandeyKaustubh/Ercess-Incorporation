//[Dashboard Javascript]

//Project:	SoftPro admin - Responsive Admin Template
//Primary use:   Used only for the main dashboard (index.html)

$(function () {

  'use strict';



		//INITIALIZE SPARKLINE CHARTS
		$(".sparkline").each(function () {
		  var $this = $(this);
		  $this.sparkline('html', $this.data());
		});

    
	
// sparkline chart
	
		$("#barchart4").sparkline([32,24,26,24,32,26,40,34,22,24], {
			type: 'bar',
			height: '100',
			width: '50%',
			barWidth: 6,
			barSpacing: 4,
			barColor: '#f44236',
		});
	
	
		
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

	
/*****E-Charts function start*****/

	
	if( $('#e_chart_1').length > 0 ){
		var eChart_1 = echarts.init(document.getElementById('e_chart_1'));
		var option8 = {
			color: ['#840fb5', '#14cc9e'],
			tooltip: {
				show: true,
				trigger: 'axis',
				backgroundColor: '#fff',
				borderRadius:20,
				padding:10,
				axisPointer:{
					lineStyle:{
						width:0,
					}
				},
				textStyle: {
					color: '#324148',
					fontFamily: '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji"',
					fontSize: 12
				}	
			},
			grid: {
				top: '3%',
				left: '3%',
				right: '3%',
				bottom: '3%',
				containLabel: true
			},
			xAxis: {
				type: 'category',
				boundaryGap: true,
				data: ['1', '2', '3', '4', '5', '6', '7','8', '9', '10', '11', '12', '13', '14'],
				axisLine: {
					show:false
				},
				axisTick: {
					show:false
				},
				axisLabel: {
					textStyle: {
						color: '#5e7d8a'
					}
				}
			},
			yAxis: {
				type: 'value',
				axisLine: {
					show:false
				},
				axisTick: {
					show:false
				},
				axisLabel: {
					textStyle: {
						color: '#5e7d8a'
					}
				},
				splitLine: {
					lineStyle: {
						color: '#eaecec',
					}
				}
			},
			series: [{
					name:'1',
					type:'bar',
					stack: 'st1',
					barMaxWidth: 20,
					data:[320, 332, 301, 334, 390, 330, 320,320, 332, 301, 334, 390, 330, 320],
					itemStyle: {
						normal: {
							barBorderRadius: [50, 50, 0, 0] ,
						}
					},
				},
				{
					name:'2',
					type:'bar',
					stack: 'st1',
					barMaxWidth: 20,
					data:[-120, -132, -101, -134, -90, -230, -210,-120, -132, -101, -134, -90, -230, -210],
					itemStyle: {
						normal: {
							barBorderRadius: [0, 0, 50, 50] ,
						}
					},

				}]
		};
		eChart_1.setOption(option8);
		eChart_1.resize();
	}
	
	if( $('#e_chart_2').length > 0 ){
		var eChart_2 = echarts.init(document.getElementById('e_chart_2'));
		var option5 = {
			color: ['#e4e7ea'],
			tooltip: {
				show: true,
				trigger: 'axis',
				backgroundColor: '#fff',
				borderRadius:6,
				padding:6,
				axisPointer:{
					lineStyle:{
						width:0,
					}
				},
				textStyle: {
					color: '#324148',
					fontFamily: '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji"',
					fontSize: 12
				}	
			},
			
			grid: {
				top: '3%',
				left: '3%',
				right: '3%',
				bottom: '3%',
				containLabel: true
			},
			xAxis : [
				{
					type : 'category',
					data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
					axisLine: {
						show:false
					},
					axisTick: {
						show:false
					},
					axisLabel: {
						textStyle: {
							color: '#5e7d8a'
						}
					}
				}
			],
			yAxis : [
				{
					type : 'value',
					axisLine: {
						show:false
					},
					axisTick: {
						show:false
					},
					axisLabel: {
						textStyle: {
							color: '#5e7d8a'
						}
					},
					splitLine: {
						lineStyle: {
							color: '#eaecec',
						}
					}
				}
			],
		   
			series: [
				{
					data:[420, 332, 401, 334, 400, 330, 410],
					type: 'bar',
					barMaxWidth: 30,
				},
				{
					data: [220, 282, 391, 300, 390, 230, 210],
					type: 'line',
					symbolSize: 6,
					itemStyle: {
						color: '#14cc9e',
					},
					lineStyle: {
						color: '#14cc9e',
						width:2,
					}
				},
				{
					data: [120, 152, 251, 124, 250, 120, 110],
					type: 'line',
					symbolSize: 6,
					itemStyle: {
						color: '#f44236',
					},
					lineStyle: {
						color: '#f44236',
						width:2,
					}
				}
			]
		};
		eChart_2.setOption(option5);
		eChart_2.resize();
	}

/*****E-Charts function end*****/

	
}); // End of use strict

