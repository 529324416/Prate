from prate import Prate, PrateWindowAppearanceConfigure

def create_prate(config:str|PrateWindowAppearanceConfigure=None, as_sub_module = True, debug=False):
    """
    Create a Prate instance with the given configuration.

    :param config: Configuration dictionary for Prate.
    :return: An instance of Prate.
    """
    
    return Prate(config, as_sub_module=as_sub_module, debug=debug)