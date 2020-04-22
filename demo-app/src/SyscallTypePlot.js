import React from 'react';
import Plot from 'react-plotly.js';
import './css/Plot.css'

const pieColors = ['#9d962f','#4f767d', '#7b8d3f', '#94384c', '#7e4e7e', '#770d09' ] 
const highlight_color = '#f9f5d7'

class SyscallTypePlot extends React.PureComponent{
    
    constructor(props){
        super(props)
        this.state = {
            values: [],
            labels: []
        }
    }

    handleValues = (data) =>{
        var i;
        let values = []
        let labels = []
        
        for (i = 0; i < data.length; i++){
            let labels_tmp = Object.keys(data[i])
            let values_tmp = Object.values(data[i])
            labels.push(labels_tmp[0])
            values.push(values_tmp[0])
        }
        this.setState({
            values: values,
            labels: labels
        })
    }
    render(){
        return(
            <Plot
                className="dist-plot"
                data={[
                {
                    values: this.state.values, 
                    labels: this.state.labels,
                    type: 'pie',
                    marker: {
                        colors: pieColors 
                    }
                }
                ]}
                layout={
                {
                    title: {
                        text: "Systemcall Distribution",
                        font: {
                            size: 24,
                            color: highlight_color 
                        }
                    },
                    legend : {
                        font : {
                            size: 18,
                            color: highlight_color
                        }
                    },
                    datarevision: this.props.value,
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)'
                }
                }
                />
        )
    }
}

export default SyscallTypePlot;
