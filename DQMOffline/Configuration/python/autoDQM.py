autoDQM = { 'common' : ['DQMOfflineCommon',
                        'DQMHarvestCommon+DQMCertCommon'],
            'commonSiStripZeroBias' : ['DQMOfflineCommonSiStripZeroBias',
                                       'DQMHarvestCommonSiStripZeroBias+DQMCertCommon'],
            'muon': ['DQMOfflineMuon',
                     'DQMHarvestMuon+DQMCertMuon'],
            'muon_miniAOD': ['DQMOfflineMuon_miniAOD',
#                             'DQMHarvestMuon_miniAOD+DQMCertMuon'],
                             'DQMHarvestMuon+DQMCertMuon'],
            'hcal':     ['DQMOfflineHcal',
                         'DQMHarvestHcal+DQMCertHcal'],
            'jetmet':  ['DQMOfflineJetMET',
                        'DQMHarvestJetMET+DQMCertJetMET'],
            'ecal':       ['DQMOfflineEcal',
                           'DQMHarvestEcal+DQMCertEcal'],
            'egamma':       ['DQMOfflineEGamma',
                           'DQMHarvestEGamma'],
            'btag':       ['DQMOfflineBTag',
                           'DQMHarvestBTag'],
            'HLTMon':     ['HLTMonitoring',
                           'HLTMonitoringClient'],
            'express':       ['@commonSiStripZeroBias+@muon+@hcal+@jetmet+@ecal',
                              '@commonSiStripZeroBias+@muon+@hcal+@jetmet+@ecal'],
            'allForPrompt':  ['@common+@muon+@hcal+@jetmet+@ecal',
                              '@common+@muon+@hcal+@jetmet+@ecal'],
            'miniAODDQM': ['DQMOfflineMiniAOD',
                        'DQMHarvestMiniAOD'],
            'standardDQM': ['DQMOffline',
                            'dqmHarvesting'],
            'sergio':['muonMiniAOD',
                      'dqmHarvesting']
            }

