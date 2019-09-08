const Plot = createPlotlyComponent(Plotly);

class Layout extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      cpuActivity: Array(12)
        .fill(0),
      coreIDs: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
      errors: []
    };
  }

  // fetch best simulations from server and update in component state
  fetchActivity() {
    fetch("/cluster/activity")
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({
            'cpuActivity': result['cpu_usage'],
          });
        },
        (error) => {
          this.setState({
            errors: ["failed to load cluster activity data"]
          });
        }
      );
  }

  fetchActivityPeriodic() {
    this.fetchActivity();
    setTimeout(this.fetchActivityPeriodic.bind(this), 1000);
  }

  componentDidMount() {
    this.fetchActivityPeriodic();
  }

  render() {
    return (
      <div className="container">
        <Plot data={[{
                type: 'bar',
                x: this.state.coreIDs,
            y: this.state.cpuActivity,
            }]}
              layout={{
                  xaxis: {
                      title : '',
                      showticklabels : false,
                  },
                  yaxis: {
                      range : [0, 100]
                  },
                  width: '100%',
                  height: '100%',
                  title: 'CPU Usage'}}
        />
      </div>
    );
  }
}

ReactDOM.render(
  <Layout />,
  document.getElementById('root')
);
