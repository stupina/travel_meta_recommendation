import os

from argparse import ArgumentParser

import pandas as pd


INPUT_DT_FORMAT = '%H-%d-%m-%Y'
OUTPUT_DT_FORMAT = '%Y-%m-%d-%H:%M'


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


def str2datetime(df, column_name):
    df[column_name] =  pd.to_datetime(df[column_name], format=INPUT_DT_FORMAT)
    return df
    

def datetime2str(df, column_name):
    df[column_name] = df[column_name].dt.strftime(OUTPUT_DT_FORMAT)
    return df


def outer_join_without_key(df1, df2):
    df1['tmp'] = 1
    df2['tmp'] = 1
    df = df1.merge(df2, on='tmp', how='outer')
    df = df.drop(columns=['tmp'])
    return df


class TravelMetaRecomendation(object):
    """
    Class provides methods for Motels.home to find maximum prices values
    """
    def __init__(self, bids_path, exchange_rate_path, motels_path):
        self.directory = os.path.dirname(os.path.abspath(__file__))
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
        err_column = 'HU'
        date_column = 'BidDate'
        counts_column = 'Counts'
        error_filter = self.bids_df[err_column].str.startswith(
            'ERROR',
            na=False,
        )

        errors_df = self.bids_df.loc[error_filter][[err_column, date_column]]
        errors_df = errors_df.groupby(
            [date_column, err_column],
        ).size().reset_index(name=counts_column)

        column_names = {
            err_column: 'Error',
        }
        errors_df = errors_df.rename(columns=column_names)

        path = f'{self.directory}/output/errors.csv'
        errors_df.to_csv(path, index=False)

        self.bids_df = self.bids_df.loc[~error_filter]

    def add_eur_rate_to_bids(self):
        """
        Adds EUR rates to bid rows
        """
        date_from = 'ValidFrom'
        date_to = 'ValidTo'
        bid_date = 'BidDate'
        self.rate_df = str2datetime(self.rate_df, date_from)
        self.bids_df = str2datetime(self.bids_df, bid_date)
        self.rate_df = datetime2str(self.rate_df, date_from)
        self.bids_df = datetime2str(self.bids_df, bid_date)

        self.rate_df= self.rate_df.sort_values(
            by=[date_from],
            ascending=True,
        )
        
        self.rate_df[date_to] = self.rate_df[date_from].shift(-1)

        self.bids_df = outer_join_without_key(self.bids_df, self.rate_df)

        self.bids_df  = self.bids_df.query(
            f'{bid_date} >= {date_from} & {bid_date} < {date_to}'
        )
        self.bids_df = self.bids_df.drop(columns=[
            date_from,
            date_to,
            'CurrencyName',
            'CurrencyCode',
        ])
    
    def transform_bids_columns(self):
        columns = [
            'MotelID',
            'BidDate',
            'US',
            'MX',
            'CA',
            'ExchangeRate',
        ]
        self.bids_df = self.bids_df[columns]

        self.bids_df = pd.melt(
            self.bids_df,
            id_vars=['MotelID', 'BidDate', 'ExchangeRate'],
            var_name='Country',
            value_name='Bid',
        )

        self.bids_df.dropna(subset=['Bid'])
        self.bids_df['BidEUR'] = self.bids_df.apply(
            lambda row: row['Bid'] * row['ExchangeRate'],
            axis=1,
        ).round(3)
    
    def prepare_bids(self):
        self.filter_and_count_erros_in_bids()
        self.add_eur_rate_to_bids()
        self.transform_bids_columns()



    def process_data(self):
        self.setup()
        self.prepare_bids()
    
    def show_info(self):
        print('bids count: ', self.bids_df.shape[0])
        print('rate count: ', self.rate_df.shape[0])
        print('motels count: ', self.motels_df.shape[0])
        print('result:\n')
        print(self.bids_df)


def main(bids_path, exchange_rate_path, motels_path):
    recomendation = TravelMetaRecomendation(
        bids_path,
        exchange_rate_path,
        motels_path,
    )
    recomendation.process_data()
    recomendation.show_info()


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