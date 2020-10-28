import React from 'react';
import Plot from 'react-plotly.js';

import './css/Plot.css'

const colors = ["#d65d0e", "#470a0a", "#1d2021"]
const highlight_color = '#f9f5d7'

export default class SyscallPlot extends React.PureComponent{

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
    //console.log(data)
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
                    datarevision : data.calls_per_second.x,
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
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

