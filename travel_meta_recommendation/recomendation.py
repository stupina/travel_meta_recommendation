from argparse import ArgumentParser

import pandas as pd


def get_headers():
    bids_header = (
        'MotelID',
        'BidDate',
        'HU',
        'UK',
        'NL',
        'US',
        'MX',
        'AU',
        'CA',
        'CN',
        'KR',
        'BE',
        'I',
        'JP',
        'IN',
        'HN',
        'GY',
        'DE',
    )
    rate_header = ('ValidFrom', 'CurrencyName', 'CurrencyCode', 'ExchangeRate')
    motels_header = ('MotelID', 'MotelName', 'Country', 'URL', 'Comment')
    return bids_header, rate_header, motels_header


class TravelMetaRecomendation(object):
    """
    Class provides methods for Motels.home to find maximum prices values
    """
    def __init__(self, bids_path, exchange_rate_path, motels_path):
        self.bids_path = bids_path
        self.exchange_rate_path = exchange_rate_path
        self.motels_path = motels_path

    
    def setup(self):
        self.bids_header, self.rate_header, self.motels_header = get_headers()
        self.bids_df, self.rate_df, self.motels_df = self.read_data()

    def read_data(self):
        bids_df = pd.read_csv(
            self.bids_path,
            header=None,
            names=self.bids_header,
        )
        rate_df = pd.read_csv(
            self.exchange_rate_path,
            header=None,
            names=self.rate_header,
        )
        motels_df = pd.read_csv(
            self.motels_path,
            header=None,
            names=self.motels_header,
        )
        return bids_df, rate_df, motels_df

    def filter_and_count_erros_in_bids(self):
        pass

    def process_data(self):
        self.setup()
        self.filter_and_count_erros_in_bids()
    
    def show(self):
        print('bids count: ', self.bids_df.shape[0])
        print('rate count: ', self.rate_df.shape[0])
        print('motels count: ', self.motels_df.shape[0])


def main(bids_path, exchange_rate_path, motels_path):
    recomendation = TravelMetaRecomendation(
        bids_path,
        exchange_rate_path,
        motels_path,
    )
    recomendation.process_data()
    recomendation.show()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-sb',
        '--bids',
        dest='bids_path',
        required=True,
    )
    parser.add_argument(
        '-se',
        '--exchange_rate',
        dest='exchange_rate_path',
        required=True,
    )
    parser.add_argument(
        '-sm',
        '--motels',
        dest='motels_path',
        required=True,
    )
    args = parser.parse_args()
    main(args.bids_path, args.exchange_rate_path, args.motels_path)