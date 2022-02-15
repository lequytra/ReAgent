#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates. All rights reserved.

import unittest

from reagent.core import types as rlt
from reagent.core.fb_checker import IS_FB_ENVIRONMENT
from reagent.core.parameters import NormalizationData, NormalizationParameters
from reagent.core.torchrec_types import PoolingType
from reagent.net_builder import discrete_dqn
from reagent.net_builder.unions import DiscreteDQNNetBuilder__Union
from reagent.preprocessing.identify_types import CONTINUOUS


if IS_FB_ENVIRONMENT:
    from reagent.fb.prediction.fb_predictor_wrapper import (
        FbDiscreteDqnPredictorWrapper as DiscreteDqnPredictorWrapper,
    )
else:
    from reagent.prediction.predictor_wrapper import DiscreteDqnPredictorWrapper


class TestDiscreteDQNNetBuilder(unittest.TestCase):
    def _test_discrete_dqn_net_builder(
        self,
        chooser: DiscreteDQNNetBuilder__Union,
        state_feature_config: rlt.ModelFeatureConfig,
        serving_module_class=DiscreteDqnPredictorWrapper,
    ) -> None:
        builder = chooser.value
        state_normalization_data = NormalizationData(
            dense_normalization_parameters={
                fi.feature_id: NormalizationParameters(
                    feature_type=CONTINUOUS, mean=0.0, stddev=1.0
                )
                for fi in state_feature_config.float_feature_infos
            }
        )
        action_names = ["L", "R"]
        q_network = builder.build_q_network(
            state_feature_config, state_normalization_data, len(action_names)
        )
        x = q_network.input_prototype()
        y = q_network(x)
        self.assertEqual(y.shape, (1, 2))
        serving_module = builder.build_serving_module(
            q_network, state_normalization_data, action_names, state_feature_config
        )
        self.assertIsInstance(serving_module, serving_module_class)

    def test_fully_connected(self) -> None:
        # Intentionally used this long path to make sure we included it in __init__.py
        # pyre-fixme[28]: Unexpected keyword argument `FullyConnected`.
        chooser = DiscreteDQNNetBuilder__Union(
            FullyConnected=discrete_dqn.fully_connected.FullyConnected()
        )
        state_feature_config = rlt.ModelFeatureConfig(
            float_feature_infos=[
                rlt.FloatFeatureInfo(name=f"f{i}", feature_id=i) for i in range(3)
            ]
        )
        self._test_discrete_dqn_net_builder(chooser, state_feature_config)

    def test_dueling(self) -> None:
        # Intentionally used this long path to make sure we included it in __init__.py
        # pyre-fixme[28]: Unexpected keyword argument `Dueling`.
        chooser = DiscreteDQNNetBuilder__Union(Dueling=discrete_dqn.dueling.Dueling())
        state_feature_config = rlt.ModelFeatureConfig(
            float_feature_infos=[
                rlt.FloatFeatureInfo(name=f"f{i}", feature_id=i) for i in range(3)
            ]
        )
        self._test_discrete_dqn_net_builder(chooser, state_feature_config)

    def test_fully_connected_with_embedding(self) -> None:
        # Intentionally used this long path to make sure we included it in __init__.py
        # pyre-fixme[28]: Unexpected keyword argument `FullyConnectedWithEmbedding`.
        chooser = DiscreteDQNNetBuilder__Union(
            FullyConnectedWithEmbedding=discrete_dqn.fully_connected_with_embedding.FullyConnectedWithEmbedding()
        )

        EMBEDDING_TABLE_SIZE = 10
        EMBEDDING_DIM = 32
        # only id_list
        state_feature_config = rlt.ModelFeatureConfig(
            float_feature_infos=[
                rlt.FloatFeatureInfo(name=str(i), feature_id=i) for i in range(1, 5)
            ],
            id_list_feature_configs=[
                rlt.IdListFeatureConfig(
                    name="A", feature_id=10, id_mapping_name="A_mapping"
                )
            ],
            id_mapping_config={
                "A_mapping": rlt.IdMappingConfig(
                    embedding_table_size=EMBEDDING_TABLE_SIZE,
                    embedding_dim=EMBEDDING_DIM,
                    hashing=False,
                    pooling_type=PoolingType.SUM,
                )
            },
        )
        self._test_discrete_dqn_net_builder(
            chooser, state_feature_config=state_feature_config
        )

        # only id_score_list
        state_feature_config = rlt.ModelFeatureConfig(
            float_feature_infos=[
                rlt.FloatFeatureInfo(name=str(i), feature_id=i) for i in range(1, 5)
            ],
            id_score_list_feature_configs=[
                rlt.IdScoreListFeatureConfig(
                    name="A", feature_id=10, id_mapping_name="A_mapping"
                )
            ],
            id_mapping_config={
                "A_mapping": rlt.IdMappingConfig(
                    embedding_table_size=EMBEDDING_TABLE_SIZE,
                    embedding_dim=EMBEDDING_DIM,
                    hashing=False,
                    pooling_type=PoolingType.SUM,
                )
            },
        )
        self._test_discrete_dqn_net_builder(
            chooser, state_feature_config=state_feature_config
        )

        # id_list + id_score_list
        state_feature_config = rlt.ModelFeatureConfig(
            float_feature_infos=[
                rlt.FloatFeatureInfo(name=str(i), feature_id=i) for i in range(1, 5)
            ],
            id_list_feature_configs=[
                rlt.IdListFeatureConfig(
                    name="A", feature_id=10, id_mapping_name="A_mapping"
                )
            ],
            id_score_list_feature_configs=[
                rlt.IdScoreListFeatureConfig(
                    name="B", feature_id=100, id_mapping_name="A_mapping"
                )
            ],
            id_mapping_config={
                "A_mapping": rlt.IdMappingConfig(
                    embedding_table_size=EMBEDDING_TABLE_SIZE,
                    embedding_dim=EMBEDDING_DIM,
                    hashing=False,
                    pooling_type=PoolingType.SUM,
                )
            },
        )
        self._test_discrete_dqn_net_builder(
            chooser, state_feature_config=state_feature_config
        )
