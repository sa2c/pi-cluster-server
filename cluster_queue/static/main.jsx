function MainPanel(props) {
  const img_src = "simulations/" + props.currentSimulation +
    "/elmeroutput0001-velomagn.png"

  return (
    <img id="result-main-image"
         src={img_src}
         alt="Simulation Main View"
         width="100%" />
  );
}

function SimulationList(props) {
  return (
    props.simulations.map((sim_id, rank) => {

      const image_url = "simulations/" + sim_id +
        "/elmeroutput0001-velomagn.png";

      const image_alt = "Simulation " + sim_id + " image";

      const additionalMainClasses =
        props.currentSimulation == sim_id ? " selected" : "";

      const additionalRankingClasses = props.showIndex ? "" : " hidden";

      return (
        <div className={"columns simulation" + additionalMainClasses}
                     key={rank}
                     id={"rank" + (sim_id + 1)}
                     onClick={ () => props.onClick(sim_id) }>

            <div
              className={"ranking column is-one-fifth" + additionalRankingClasses}
            >
            <h2>
              { rank + 1 }
            </h2>
          </div>

          <div className="simulation-data">

            <img src={image_url}
                 alt={image_alt}
                 width="100%" />

            <div className="simulation-info">
              <p>Mark</p>
              <p>Drag: 1.3354</p>
            </div>
          </div>
          </div>
      )
    })
  );
}

class Layout extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      bestSimulations: [1, 3, 2, 1, 3, 4, 1],
      recentSimulations: [3, 1, 2, 1, 5, 1, 3],
      currentSimulation: 1
    };
  }

  simulationChoiceHandler(sim_id) {
    this.setState({
      currentSimulation: sim_id
    });
  }

  render() {
    return (
      <div className="container">
              <div className="columns">
                <div className="column is-two-thirds is-vertical-centre">
                  <MainPanel currentSimulation={this.state.currentSimulation}/>
                </div>
                <div id="leaderboard" className="column is-scroll">
                  <h2>Leaderboard</h2>
                  <SimulationList showIndex={ true }
                                  simulations={ this.state.bestSimulations }
                                  currentSimulation={this.state.currentSimulation}
                                  onClick={ this.simulationChoiceHandler.bind(this) }/>
                </div>
                <div id="recent-simulations" className="column is-scroll">
                  <h2>Recent</h2>
                  <SimulationList showIndex={ false }
                                  simulations={ this.state.recentSimulations }
                                  currentSimulation={this.state.currentSimulation}
                                  onClick={ this.simulationChoiceHandler.bind(this) }/>
                </div>
              </div>
            </div>
    );
  }
}

ReactDOM.render(
  <Layout />,
  document.getElementById('root')
);
