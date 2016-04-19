

var myChart=echarts.init(document.getElementById('status'));

option = {
    tooltip: {
	trigger: 'item',
	formatter: "{a} <br/>{b}: {c} ({d}%)"
    },
    legend: {
	orient: 'vertical',
	x: 'left',
	data:['accept','reject','unaccept']
    },
    series: [
    {
	type:'pie',
	radius: ['50%', '70%'],
	avoidLabelOverlap: false,
	label: {
	    normal: {
		show: false,
		position: 'center'
	    },
	    emphasis: {
		show: true,
		textStyle: {
		    fontSize: '30',
		    fontWeight: 'bold'
		}
	    }
	},
	labelLine: {
	    normal: {
		show: false
	    }
	},
	data:[
	{value:{{ accept_num }}, name:'accept', itemStyle:{
						 normal:{color:'green'}
					     }},

	{value:{{ reject_num }}, name:'reject', itemStyle:{
						 normal:{color:'red'}
					     }},
	    {value:{{ unaccept_num }}, name:'unaccept', itemStyle:{
						       normal:{color:'yellow'}
						   }},
	]
    }
    ]
};
myChart.setOption(option);
