//[Dashboard Javascript]

//Project:	SoftPro admin - Responsive Admin Template
//Primary use:   Used only for the main dashboard (index.html)

$(function () {

  'use strict';
	
	$('#tickets').DataTable({
	  'paging'      : true,
	  'lengthChange': false,
	  'searching'   : false,
	  'ordering'    : true,
	  'info'        : true,
	  'autoWidth'   : false,
	});

    // LINE CHART
    let btc = new Morris.Line({
        element: 'mor-1',
        resize: true,
        data: [{
                y: '2011',
                item1: 4912
            },
            {
                y: '2012',
                item1: 3767
            },
            {
                y: '2013',
                item1: 6810
            },
            {
                y: '2014',
                item1: 5670
            },
            {
                y: '2015',
                item1: 4820
            },
            {
                y: '2016',
                item1: 15073
            },
            {
                y: '2017',
                item1: 10687
            },
            {
                y: '2018',
                item1: 8432
            }, {
                y: '2019',
                item1: 2666
            },
            {
                y: '2020',
                item1: 15778
            },
        ],
        xkey: 'y',
        ykeys: ['item1'],
        labels: ['Bitcoin'],
        gridLineColor: 'transparent',
        lineColors: ['#fff'],
        lineWidth: 3,
        hideHover: 'auto',
        pointSize: 0,
        axes: false
    });

    // LINE CHART
    let eth = new Morris.Line({
        element: 'mor-2',
        resize: true,
        data: [{
                y: '2011',
                item1: 4912
            },
            {
                y: '2012',
                item1: 3767
            },
            {
                y: '2013',
                item1: 6810
            },
            {
                y: '2014',
                item1: 5670
            },
            {
                y: '2015',
                item1: 4820
            },
            {
                y: '2016',
                item1: 15073
            },
            {
                y: '2017',
                item1: 10687
            },
            {
                y: '2018',
                item1: 8432
            }, {
                y: '2019',
                item1: 2666
            },
            {
                y: '2020',
                item1: 15778
            },
        ],
        xkey: 'y',
        ykeys: ['item1'],
        labels: ['Bitcoin'],
        gridLineColor: 'transparent',
        lineColors: ['#fff'],
        lineWidth: 3,
        hideHover: 'auto',
        pointSize: 0,
        axes: false
    });

    // LINE CHART
    let rpl = new Morris.Line({
        element: 'mor-3',
        resize: true,
        data: [{
                y: '2011',
                item1: 4912
            },
            {
                y: '2012',
                item1: 3767
            },
            {
                y: '2013',
                item1: 6810
            },
            {
                y: '2014',
                item1: 5670
            },
            {
                y: '2015',
                item1: 4820
            },
            {
                y: '2016',
                item1: 15073
            },
            {
                y: '2017',
                item1: 10687
            },
            {
                y: '2018',
                item1: 8432
            }, {
                y: '2019',
                item1: 2666
            },
            {
                y: '2020',
                item1: 15778
            },
        ],
        xkey: 'y',
        ykeys: ['item1'],
        labels: ['Bitcoin'],
        gridLineColor: 'transparent',
        lineColors: ['#fff'],
        lineWidth: 3,
        hideHover: 'auto',
        pointSize: 0,
        axes: false
    });
    // LINE CHART
    let ltc = new Morris.Line({
        element: 'mor-4',
        resize: true,
        data: [{
                y: '2011',
                item1: 4912
            },
            {
                y: '2012',
                item1: 3767
            },
            {
                y: '2013',
                item1: 6810
            },
            {
                y: '2014',
                item1: 5670
            },
            {
                y: '2015',
                item1: 4820
            },
            {
                y: '2016',
                item1: 15073
            },
            {
                y: '2017',
                item1: 10687
            },
            {
                y: '2018',
                item1: 8432
            }, {
                y: '2019',
                item1: 2666
            },
            {
                y: '2020',
                item1: 15778
            },
        ],
        xkey: 'y',
        ykeys: ['item1'],
        labels: ['Bitcoin'],
        gridLineColor: 'transparent',
        lineColors: ['#fff'],
        lineWidth: 3,
        hideHover: 'auto',
        pointSize: 0,
        axes: false
    });
	
	
	
	
	if( $('#e_chart_2').length > 0 ){
		var eChart_2 = echarts.init(document.getElementById('e_chart_2'));
		var option5 = {
			color: ['#f4c22b'],
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

