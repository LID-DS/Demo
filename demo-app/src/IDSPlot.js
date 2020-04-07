import React from 'react';
import Plot from 'react-plotly.js';

import './css/IDSPlot.css'

const colors = ["#236845", "#8C1217"]

export default class IDSPlot extends React.PureComponent{

    // recieves data from App.js which implements websocket
    // calculate window for plotly fill

    render(){
        return(
            <PlotRenderer data={this.props}/>
        )
    };
    
}


function PlotRenderer(data) {
    data = data.data.plot_info
    if(data.plot_type === "syscall"){
        return(
		<Plot
		    data={[
			{
			    x: data.calls_per_second.x,
			    y: data.calls_per_second.y,
			    mode: 'markers',
			    type: 'scatter'
			}
		    ]}
		    layout = {
			{
			    title : "Systemcalls in container",
			    xaxis : {
				title : "Seconds"
			    },
			    yaxis : {
				title : "Amount of Systemcalls"
			    },
			    datarevision : data.index,
			    paper_bgcolor: 'rgba(0,0,0,0)',
			    plot_bgcolor: 'rgba(0,0,0,0)'

			}
		    }
		/>
        )
    }
    else if (data.plot_type === "ids"){
        return(
		<Plot
		    data={[
			{
			    x: data.ids_score.x,
			    y: data.ids_score.y,
			    mode: 'markers',
			    type: 'scatter',
                marker: {
                    color: colors[data.alarm ? 1 : 0 ]
                }
			}
		    ]}
		    layout = {
			{
			    title : "IDS-Score",
			    xaxis : {
                    title : "Seconds"
			    },
			    yaxis : {
                    title : "Highest Score In Last Second"
			    },
			    datarevision : data.index,
			    paper_bgcolor: 'rgba(0,0,0,0)',
			    plot_bgcolor: 'rgba(0,0,0,0)',
                shapes: [
                    {
                        type: 'line',
                        y0: data.slider_threshold,
                        y1: data.slider_threshold,
                        x0: data.ids_score.x[0],
                        x1: data.index,
                        line:{
                            color: 'rgb(140,18,23)',
                            width: 2
                        }
                    }
                ]
			}
		    }
		/>
        )
    }
}

