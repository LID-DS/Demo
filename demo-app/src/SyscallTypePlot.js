import React from 'react';
import Plot from 'react-plotly.js';
import './css/Plot.css'

const pieColors = ['rgb(56,75,126)','rgb(18,36,37)', 'rgb(34,53,101)', 'rgb(99,79,37)', 'rgb(124,103,37)' ] 

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
        console.log(this.state.values)
        console.log(this.state.labels)
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
