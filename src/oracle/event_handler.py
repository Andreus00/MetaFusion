from .events import *

def initOracleFilters(contract):
    """
        Init the president event filters:
            event PacketForged(address indexed blacksmith, uint32 packetUUid);
            event PacketOpened(address indexed opener, uint32[] prompts);
            event CreateImage(address indexed creator, uint256 prompts);
            event willToBuyPacket(address buyer, address seller, uint256 id, uint256 value);
            event willToBuyPrompt(address buyer, address seller, uint256 id, uint256 value);
            event willToBuyImage(address buyer, address seller, uint256 id, uint256 value);
            event PromptTransfered(address indexed buyer, address indexed seller, uint256 id);
            event PacketTransfered(address indexed buyer, address indexed seller, uint256 id);
            event CardTransfered(address indexed buyer, address indexed seller, uint256 id);
    """
    filters = [
        contract.events.PacketOpened.create_filter(fromBlock="latest"),
        contract.events.CreateImage.create_filter(fromBlock="latest"),
        contract.events.WillToBuyPacket.create_filter(fromBlock="latest"),
        contract.events.WillToBuyPrompt.create_filter(fromBlock="latest"),
        contract.events.WillToBuyImage.create_filter(fromBlock="latest"),
    ]

    return filters

def handle_event(event, provider, contract, IPFSClient, model, con):
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
    
    event_object.handle(contract, provider, IPFSClient, model, con)
