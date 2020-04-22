import React from 'react';
import Plot from 'react-plotly.js';

import './css/Plot.css'

const colors = ["#d65d0e", "#470a0a", "#1d2021"]
const highlight_color = '#f9f5d7'

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
            className="syscall-plot"
		    data={[
			{
			    x: data.calls_per_second.x,
			    y: data.calls_per_second.y,
			    mode: 'markers',
			    type: 'scatter',
                marker: {
                    color: colors[2] 
                }
			}
		    ]}
		    layout = {
			{
			    title : {
                    text: "Systemcalls in container",
                    font: {
                        size: 24,
                        color: '#f9f5d7'
                    }
                },
			    xaxis : {
                    title : {
                        text: "Seconds",
                        font: {
                            size: 18,
                            color: '#f9f5d7'
                        }
                    }
			    },
			    yaxis : {
                    title : {
                        text: "Amount of Systemcalls",
                        font: {
                            size: 18,
                            color: '#f9f5d7'
                        }
                    },
                    zerolinecolor: highlight_color, 
                    gridcolor: highlight_color, 
                    showgrid: true,
                    tickcolor: highlight_color 
			    },
			    datarevision : data.index,
			    paper_bgcolor: 'rgba(0,0,0,0)',
			    plot_bgcolor: 'rgba(0,0,0,0)',
                //plot_bgcolor: '#aaaaaa',
                //bordercolor: '#000000',
                legend: {
                    font: {
                        size: 12,
                        color: highlight_color 
                    }
                }

			}
		    }
		/>
        )
    }
    else if (data.plot_type === "ids"){
        return(
		<Plot
            className="ids-plot"
		    data={[
                {
                    x: data.ids_score.x,
                    y: data.ids_score.y,
                    mode: 'markers',
                    type: 'scatter',
                    marker: {
                        color: colors[data.ids_score.alarm ? 1 : 0 ]
                    }
                }
		    ]}
		    layout = {
			{
			    title : {
                    text: "IDS-Score",
                    font: {
                        size: 24,
                        color: highlight_color 
                    }
                },
			    xaxis : {
                    title : {
                        text: "Seconds",
                        font: {
                            size: 18,
                            color: highlight_color 
                        }
                    }
			    },
			    yaxis : {
                    title : {
                        text: "Highest Score In Last Second",
                        font: {
                            size: 18,
                            color: highlight_color 
                        }
                    }
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
                            color: 'rgb(179,22,22)',
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

