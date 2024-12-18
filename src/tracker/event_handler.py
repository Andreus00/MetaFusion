from .events import *

def initTrackerFilters(contract):
    """
        Init the tracker's event filters
    """
    filters = [
        contract.events.PacketForged.create_filter(fromBlock="latest"),
        contract.events.PacketOpened.create_filter(fromBlock="latest"),
        contract.events.CreateImage.create_filter(fromBlock="latest"),
        contract.events.PromptCreated.create_filter(fromBlock="latest"),
        contract.events.ImageCreated.create_filter(fromBlock="latest"),
        contract.events.DestroyImage.create_filter(fromBlock="latest"),
        contract.events.PromptTransfered.create_filter(fromBlock="latest"),
        contract.events.PacketTransfered.create_filter(fromBlock="latest"),
        contract.events.CardTransfered.create_filter(fromBlock="latest"),
        contract.events.UpdateListPrompt.create_filter(fromBlock="latest"),
        contract.events.UpdateListPacket.create_filter(fromBlock="latest"),
        contract.events.UpdateListImage.create_filter(fromBlock="latest"),
    ]

    return filters

def handle_event(event, provider, contract, IPFSClient, data, logger):
    '''
    New event: AttributeDict({
                'args': AttributeDict({
                    'opener': '0x70997970C51812dc3A010C7d01b50e0d17dc79C8', 
                    'prompts': [172033, 537042945, 1073872897, 1610743809, 2147639297, 2684518401, 3221381121, 3758243841]
                    }), 
                'event': 'PacketOpened', 
                'logIndex': 9, 
                'transactionIndex': 0, 
                'transactionHash': HexBytes('0x482ac99b4d598f74e854199f8d3596116154cb0ee2300506de80693d8743f244'), 
                'address': '0x5FbDB2315678afecb367f032d93F642f64180aa3', 
                'blockHash': HexBytes('0x3cc6db0d32783b2bb5de4c97d19d63f7ba72db81e6e4c249256bd45850cb2a93'), 
                'blockNumber': 13}
                )
    '''
    event_name = event.event
    event_args = event.args

    event_class = get_event_class(event_name)
    kwargs = dict(event_args)
    kwargs['event'] = event_name
    event_object = event_class(**kwargs)
    event_object.handle(contract, provider, IPFSClient, data)
    event_object.log(logger)
