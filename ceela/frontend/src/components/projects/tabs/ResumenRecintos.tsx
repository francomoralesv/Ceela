import { EnergySystemSelection } from '@/types/energySystem';
import React, { useEffect, useState } from 'react';
import { Col, Nav, Row, Tab } from 'react-bootstrap';
import CasoBaseTable from '../recinto/CasoBaseTable';
import EnergySystemSelectors, { ConfigState } from '../recinto/EnergySystemSelectors';
import TablaConsumos from '../recinto/TablaConsumos';
import TablaDemandas from '../recinto/TablaDemandas';
import TablaDisconfort from '../recinto/TablaDisconfort';
import TablaEmisiones from '../recinto/TablaEmisiones';

interface ResumenRecintosProps {
  globalResults: any;
  onUpdated?: (data: any) => void;
}


const ResumenRecintos: React.FC<ResumenRecintosProps> = ({ globalResults, onUpdated }) => {
  const [config, setConfig] = useState<ConfigState>({
    energySystems: [],
    rendimientoCalef: [],
    distribucionHvac: [],
    controlHvac: [],
    rendimientoRef: [],
    consumosEnergia: []
  });

  const [enclosures, setEnclosures] = useState<any[]>([]);
  const [energyConfig, setEnergyConfig] = useState<EnergySystemSelection>({
    combustibleCalef: null,
    rendimientoCalef: null,
    distribucionCalef: null,
    distribucionRef: null,
    controlCalef: null,
    combustibleRef: null,
    rendimientoRef: null,
    controlRef: null
  });

  // Only update enclosures from globalResults
  useEffect(() => {
    if (globalResults?.result_by_enclosure_v2) {
      setEnclosures(globalResults.result_by_enclosure_v2);
    }
  }, [globalResults]);

  const onUpdate = (recintos: any[]) => {
    onUpdated?.(recintos);
  }

  return (
    <div className="container-fluid mt-4">
      <div>
        <Tab.Container id="tabs-recintos" defaultActiveKey="demanda">
          <Row className="mb-5">
            <Col sm={12}>
              <Nav variant="pills" className="flex-row">
                <Nav.Item>
                  <Nav.Link className="nav-pill-info" eventKey="demanda">
                    Demanda
                  </Nav.Link>
                </Nav.Item>
                <Nav.Item>
                  <Nav.Link className="nav-pill-info" eventKey="consumo">
                    Consumo
                  </Nav.Link>
                </Nav.Item>
                <Nav.Item>
                  <Nav.Link className="nav-pill-info" eventKey="co2">
                    CO2_eq
                  </Nav.Link>
                </Nav.Item>
                <Nav.Item>
                  <Nav.Link eventKey="disconfort" className="nav-pill-info">
                    Hrs Disconfort T° Libre
                  </Nav.Link>
                </Nav.Item>
                <Nav.Item>
                  <Nav.Link eventKey="base" className="nav-pill-info">
                    Caso Base
                  </Nav.Link>
                </Nav.Item>
              </Nav>
            </Col>
          </Row>
          <Row className="gx-5 justify-content-between">
            <Col sm={12}>
              <Tab.Content>
                <Tab.Pane eventKey="demanda" className="overflow-x-scroll">
                  <TablaDemandas recintos={enclosures} />
                </Tab.Pane>
                <Tab.Pane eventKey="consumo" className="overflow-x-scroll">
                  <TablaConsumos
                    combustibleCalef={energyConfig.combustibleCalef}
                    config={{
                      recintos: enclosures,
                      ...config,
                      consumosEnergia: config.consumosEnergia
                    }}
                  />
                </Tab.Pane>
                <Tab.Pane eventKey="co2" className="overflow-x-scroll">
                  <TablaEmisiones
                    recintos={enclosures}
                    combustibleCalef={energyConfig.combustibleCalef}
                    consumosEnergia={config.consumosEnergia}
                    onUpdate={onUpdate}
                  />
                </Tab.Pane>
                <Tab.Pane eventKey="disconfort" className="overflow-x-scroll">
                  <TablaDisconfort recintos={enclosures} />
                </Tab.Pane>
                <Tab.Pane eventKey="base" className="overflow-x-scroll">
                  <CasoBaseTable
                    recintos={enclosures}
                    combustibleCalef={energyConfig.combustibleCalef}
                    consumosEnergia={config.consumosEnergia}
                    onUpdate={onUpdate}
                  />
                </Tab.Pane>
              </Tab.Content>
            </Col>
          </Row>
        </Tab.Container>
      </div>
    </div>
  );
};

export default ResumenRecintos;