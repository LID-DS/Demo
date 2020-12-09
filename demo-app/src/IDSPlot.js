import React from 'react';
import Plot from 'react-plotly.js';

import './css/Plot.css'

const colors = ["#d65d0e", "#470a0a", "#1d2021", "#243842"]
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
    data = data.data
    if(data.time.length > 0){
        if(!data.multiple_active){
            let score
            let scatter_color = 0
            if(data.type === 'mlp'){
                score = data.score2
                scatter_color = 3
            }
            else if (data.type === 'stide') {
                score = data.score
            }
            else if (data.type === 'multiple'){
                return(<div>multiple</div>)
            }
            return(
                <Plot
                    className="ids-plot"
                    data={[
                        {
                            x: data.time,
                            y: score,
                            mode: 'markers',
                            type: 'scatter',
                            marker: {
                                color: colors[data.alarm ? 1 : scatter_color ]
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
                        datarevision: data.time,
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        shapes: [
                            {
                                type: 'line',
                                y0: data.threshold,
                                y1: data.threshold,
                                x0: data.time[0],
                                x1: data.time[data.time.length-1],
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
        else if(data.multiple_active){
            //console.log(data.data)
            let stide_score = data.score
            let mlp_score = data.score2
            return (
                <Plot
                    className="ids-plot"
                    data={[
                        {
                            x: data.time,
                            y: stide_score,
                            mode: 'markers',
                            type: 'scatter',
                            marker: {
                                color: colors[data.alarm_of==='stide' && data.alarm ? 1 : 0 ]
                            },
                            name: 'Stide'
                        },
                        {
                            x: data.time,
                            y: mlp_score,
                            mode: 'markers',
                            type: 'scatter',
                            marker: {
                                color: colors[data.alarm_of==='mlp' && data.alarm ? 1 : 3 ]
                            },
                            name: 'MLP'
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
                        datarevision: data.time,
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        shapes: [
                            {
                                type: 'line',
                                y0: data.threshold,
                                y1: data.threshold,
                                x0: data.time[0],
                                x1: data.time[data.time.length-1],
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
    else {
        return(<div>Loading...</div>)
    }
}

