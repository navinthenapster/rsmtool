"""
Classes for writing DataContainer
DataFrames to files.

:author: Jeremy Biggs (jbiggs@ets.org)
:author: Anastassia Loukina (aloukina@ets.org)
:author: Nitin Madnani (nmadnani@ets.org)

:date: 10/25/2017
:organization: ETS
"""

from os import makedirs
from os.path import join


class DataWriter:
    """
    A DataWriter class to write out
    DataContainer objects
    """

    def __init__(self, experiment_id=None):
        """
        """
        self._id = experiment_id

    def write_experiment_output(self,
                                csvdir,
                                data_container,
                                dataframe_names=None,
                                new_names_dict=None,
                                include_experiment_id=True,
                                reset_index=False,
                                file_format='csv',
                                index=False,
                                **kwargs):
        """
        Write out each of the given list of data frames as a ``.csv``, ``.json`` or
        ``.xlsx`` file in the given directory. Each data frame was generated
        as part of running an RSMTool experiment. All files are prefixed with
        the given experiment ID and suffixed with either the name of the data
        frame in the DataContainer object, or a new name if ``new_names_dict`` is
        specified. Additionally, the indexes in the data frames are reset if
        so specified.

        Parameters
        ----------
        csvdir : str
            Path to the `output` experiment sub-directory that will
            contain the CSV files corresponding to each of the data frames.
        data_container : container.DataContainer
            A DataContainer object.
        dataframe_names : list of str, optional
            List of data frame names, one for each of the data frames.
        new_names_dict : dict, optional
            New dictionary with new names for the data frames, if desired.
            Defaults to None.
        include_experiment_id : str, optional
            Whether to include the experiment ID in the file name.
            Defaults to True.
        reset_index : bool, optional
            Whether to reset the index of each data frame
            before writing to disk. Defaults to `False`.
        file_format : {'csv', 'excel', 'json'}, optional
            The file format in which to output the data.
            Defaults to 'csv'.
        index : bool
            Whether to include index.
            Defaults to False.

        Raises
        ------
        KeyError
            If file_format is not correct.
        """

        # If no frames specified, get all frames in data container

        data_container = data_container.copy()

        # If no `dataframe_names` specified, use all names
        if dataframe_names is None:
            dataframe_names = data_container.keys()

        # Otherwise, check to make sure all specified names
        # are actually in the DataContainer
        else:
            for name in dataframe_names:
                if name not in data_container:
                    raise KeyError('The name `{}` is not in the container.'
                                   ''.format(name))

        # Loop through DataFrames, and save
        # output in specified format
        for dataframe_name in dataframe_names:

            df = data_container.get_frame(dataframe_name)
            if df is None:
                raise KeyError('The DataFrame `{}` does not exist.'.format(dataframe_name))

            # If the DataFrame is empty, skip it
            if df.empty:
                continue

            # If there is a desire to rename some DataFrames,
            # get the new name
            if new_names_dict is not None:
                if dataframe_name in new_names_dict:
                    dataframe_name = new_names_dict[dataframe_name]

            # Reset the index, if desired
            if reset_index:
                df.index.name = ''
                df.reset_index(inplace=True)

            # If include_experiment_id is True, and the experiment_id exists
            # include it in the file name; otherwise, do not include it.
            if include_experiment_id and self._id is not None:
                outfile = join(csvdir, '{}_{}'.format(self._id, dataframe_name))
            else:
                outfile = join(csvdir, dataframe_name)

            # Save a copy of the frame to the output directory
            # in the specified format
            file_format = file_format.lower()

            if file_format == 'csv':
                outfile += '.csv'
                df.to_csv(outfile, index=index, **kwargs)

            elif file_format == 'json':
                outfile += '.json'
                df.to_json(outfile, orient='records', **kwargs)

            elif (file_format == 'excel' or
                  file_format == 'xlsx'):
                outfile += '.xlsx'
                df.to_excel(outfile, index=index, **kwargs)

            else:
                raise KeyError('Please make sure that the `file_format` specified '
                               'is one of the following:\n{`json`, `csv`, `excel`}\n.'
                               'You specified {}.'.format(file_format))

    def write_feature_csv(self,
                          featuredir,
                          data_container,
                          selected_features,
                          include_experiment_id=True,):
        """
        Write out the feature file to disk.

        Parameters
        ----------
        featuredir : str
            Path to the `feature` experiment output directory where the
            feature JSON file will be saved.
        data_container : container.DataContainer
            A DataContainer object.
        selected_features : list of str
            List of features that were selected for model building.
        include_experiment_id : str, optional
            Whether to include the experiment ID in the file name.
            Defaults to True.
        """

        df_feature_specs = data_container['feature_specs']

        # Select specific features used in training
        df_selected = df_feature_specs[df_feature_specs['feature'].isin(selected_features)]

        # Replace existing `feature_specs` with selected features specs
        data_container.add_dataset({'frame': df_selected,
                                    'name': 'feature_specs'}, update=True)

        makedirs(featuredir, exist_ok=True)
        self.write_experiment_output(featuredir,
                                     data_container,
                                     ['feature_specs'],
                                     {'feature_specs': 'selected'},
                                     include_experiment_id=include_experiment_id)
