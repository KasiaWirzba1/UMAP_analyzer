import flowio
import numpy as np


class FlowCytometryPreprocessor:

    @staticmethod
    def load_fcs(fcs_path: str) -> np.ndarray:
        fd = flowio.FlowData(fcs_path)
        data = fd.as_array(preprocess=True)
        return data

    @staticmethod
    def load_sample_pair(stained_path: str, control_path: str, skip_first_n: int = 2):
        # Load stained
        fd_stained = flowio.FlowData(stained_path)
        stained_data = fd_stained.as_array(preprocess=True)
        print(f"Stained data shape: {stained_data.shape}")

        # Load control
        fd_control = flowio.FlowData(control_path)
        control_data = fd_control.as_array(preprocess=True)
        control_median = np.median(control_data, axis=0)
        print(f"Control data shape: {control_data.shape}")

        # Skip FSC, SSC
        stained_clean = stained_data[:, skip_first_n:]
        control_clean = control_median[skip_first_n:]

        return stained_clean, control_clean

    @staticmethod
    def preprocess_data(stained_data: np.ndarray, control_median: np.ndarray, cofactor: float = 150.0):

        # Background subtraction
        background_subtracted = stained_data - control_median
        background_subtracted = np.maximum(background_subtracted, 0)

        # Arcsinh transform
        umap_data = np.arcsinh(background_subtracted / cofactor).astype(np.float32)

        return umap_data

    @staticmethod
    def full_pipeline(stained_path: str, control_path: str, cofactor: float = 150.0):

        # Load
        stained_data, control_median = FlowCytometryPreprocessor.load_sample_pair(
            stained_path, control_path
        )

        # Preprocess
        umap_data = FlowCytometryPreprocessor.preprocess_data(
            stained_data, control_median, cofactor
        )

        return umap_data