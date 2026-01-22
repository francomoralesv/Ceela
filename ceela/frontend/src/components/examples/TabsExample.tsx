import HorizontalTabs from '@/components/common/HorizontalTabs';
import TableTabs from '@/components/common/TableTabs';
import { useState } from 'react';

/**
 * Ejemplo de uso de componentes de tabs modernos
 */
const TabsExample = () => {
    const [currentTab, setCurrentTab] = useState('tab1');
    const [tableTab, setTableTab] = useState('table1');

    const tabs = [
        { key: 'tab1', label: 'Información General' },
        { key: 'tab2', label: 'Configuración' },
        { key: 'tab3', label: 'Estadísticas' }
    ];

    const tableTabs = [
        { key: 'table1', label: 'Activos' },
        { key: 'table2', label: 'Histórico' },
        { key: 'table3', label: 'Archivados' }
    ];

    return (
        <div className="container mt-5">
            <h3>Ejemplo de Tabs Horizontales</h3>
            <div className="card p-4 shadow-sm">
                <HorizontalTabs
                    tabs={tabs}
                    currentTab={currentTab}
                    onTabChange={setCurrentTab}
                />

                <div className="tab-content mt-4">
                    {currentTab === 'tab1' && (
                        <div>
                            <h4>Información General</h4>
                            <p>Este es el contenido de la pestaña de Información General.</p>
                        </div>
                    )}
                    {currentTab === 'tab2' && (
                        <div>
                            <h4>Configuración</h4>
                            <p>Este es el contenido de la pestaña de Configuración.</p>
                        </div>
                    )}
                    {currentTab === 'tab3' && (
                        <div>
                            <h4>Estadísticas</h4>
                            <p>Este es el contenido de la pestaña de Estadísticas.</p>
                        </div>
                    )}
                </div>
            </div>

            <h3 className="mt-5">Ejemplo de Tabs para Tablas</h3>
            <div className="card shadow-sm">
                <div className="card-header bg-light">
                    <TableTabs
                        tabs={tableTabs}
                        initialTab={tableTab}
                        onTabChange={setTableTab}
                    />
                </div>
                <div className="card-body">
                    {tableTab === 'table1' && (
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Nombre</th>
                                    <th>Estado</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>1</td>
                                    <td>Proyecto A</td>
                                    <td>Activo</td>
                                </tr>
                                <tr>
                                    <td>2</td>
                                    <td>Proyecto B</td>
                                    <td>Activo</td>
                                </tr>
                            </tbody>
                        </table>
                    )}
                    {tableTab === 'table2' && (
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Nombre</th>
                                    <th>Fecha</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>1</td>
                                    <td>Proyecto C</td>
                                    <td>10/01/2025</td>
                                </tr>
                                <tr>
                                    <td>2</td>
                                    <td>Proyecto D</td>
                                    <td>15/02/2025</td>
                                </tr>
                            </tbody>
                        </table>
                    )}
                    {tableTab === 'table3' && (
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Nombre</th>
                                    <th>Archivado</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>1</td>
                                    <td>Proyecto E</td>
                                    <td>01/03/2025</td>
                                </tr>
                                <tr>
                                    <td>2</td>
                                    <td>Proyecto F</td>
                                    <td>20/04/2025</td>
                                </tr>
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
};

export default TabsExample;
