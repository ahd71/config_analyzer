from homeassistant.core import HomeAssistant #, ServiceCall, callback

import logging
import networkx as nx
import matplotlib.pyplot as plt

from ..const import DOMAIN

from homeassistant.helpers import (
    config_validation as cv,
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
)

_LOGGER = logging.getLogger(__name__)

class PluginClass:
    def get_name(self):
        return "Gephi Exporter"

    def get_release(self):
        return "0.23"

    async def execute(self, hass: HomeAssistant, argument1):

        try:
            G = nx.DiGraph()

            # area
            area_registry = ar.async_get(hass)

            for node_id, item in area_registry.areas.items():
                G.add_node(
                    node_id,  # the id of the node
                    type="area",
                    debug='1',
                    label=item.name or "(no name)",
                )

            # devices
            device_registry = dr.async_get(hass)
            _LOGGER.debug('DEVICE......')

            for node_id, item in device_registry.devices.items():
                _LOGGER.debug(node_id)
                G.add_node(
                    node_id,  # the id of the node
                    type="device",
                    debug='2',
                    label=item.name_by_user or item.name or "(no name)",
                )
                G.add_edge(node_id, item.area_id or "(no area)", debug='3')

            # entities
            entity_registry = er.async_get(hass)
            _LOGGER.debug('ENTITIES......')

            for node_id, item in entity_registry.entities.items():
                G.add_node(
                    item.id,
                    stdid = item.id,
                    type="entity",
                    debug='4',
                    entity_id=item.entity_id,
                    platform=item.platform,
                    label=item.name or item.original_name or item.entity_id or "(no name)",
                )  # label in this lingo, but name in HA lingo
                if item.device_id is not None:
                    G.add_edge(item.id, item.device_id, debug='5')
                G.add_node( # todo: a bit dirty to add it on every reference but unsure how to iterate thru integrations at this point in time
                    item.platform, #TODO: ideally an id if it exist
                    type="platform",
                    debug='10',
                    platform=item.platform,
                    label=item.platform,
                )

            for (
                x
            ) in (
                hass.config_entries.async_entries()
            ):  # todo: find correct method to not use protected member and do it async

                _LOGGER.debug(x.entry_id)

                G.add_node(
                    #x.entry_id,  # the id of the node
                    x.entry_id,  # the id of the node
                    unique_id = x.unique_id or '(None)',
                    type="**** X",
                    debug = '7',
                    label=x.title or "(no name)", # todo: resolve more names, like orginal etc?
                )  # label in this lingo, but name in HA lingo

                xentities = x.options.get("entities", None)
                if xentities is not None:
                    for m in xentities:
                        _LOGGER.debug(m)
                        m2 = m # todo: temp
                        m2 =  entity_registry.async_get(m) # TODO : DOESN'T WORK YET.... or does it?

                        if m2 is not None:
                            _LOGGER.debug(m2.id or '(none)')

                            G.add_node(
                                m2.id,  # the id of the node
                                type="**** M2",
                                unique_id = m2.unique_id or '(None)',
                                debug = '8',
                                label=m2.name or m2.original_name or "(no name)",
                            )
                            _LOGGER.debug(x.entry_id)
                            _LOGGER.debug(m2.id)

                            G.add_edge(x.entry_id, m2.id, debug='9')


            path = hass.config.path()

            gexf_file_path = (
                path
                + '/custom_components/' + DOMAIN + '/output/'
                + 'home assistant configuration.gexf'
            )
            _LOGGER.debug('---- S3')
            nx.write_gexf(
                G,
                gexf_file_path,
                version="1.2draft",
                encoding="utf-8",
                prettyprint=True,
            )
            _LOGGER.debug('---- S4')

            # generate html graph
            _LOGGER.debug('generate html graph starting')
            subgraph = G #.subgraph([node_to_query] + connected_nodes)

            node_labels = {node: f'{node}' for node in subgraph.nodes()}

            data = subgraph.nodes.items()

            for node_id, attributes in data:
                label = attributes.get('label', node_id)
                node_labels[node_id] = label

            # Plot the subgraph with node labels
            pos = nx.spring_layout(subgraph)
            plt.figure(figsize=(8, 6))
            pos = nx.spring_layout(subgraph, seed=42, iterations=100)
            _LOGGER.debug('Z2')
            nx.draw(subgraph,
                    pos,
                    with_labels=True,
                    labels=node_labels,
                    node_color='lightblue',
                    node_size=1000,
                    font_size=12,
                    font_weight='bold')
            _LOGGER.debug('Z3')
            plt.title(f"Configuration Graph")
            _LOGGER.debug('Z4')
            #plt.show()
            _LOGGER.debug('Z5')
            plt.savefig(path + '/custom_components/' + DOMAIN + '/output/' + 'dyngraph.svg', format='svg')
            _LOGGER.debug('generate html graph completed')
            return "Successful"
        except Exception as e:
            return f"Error: {str(e)}"
