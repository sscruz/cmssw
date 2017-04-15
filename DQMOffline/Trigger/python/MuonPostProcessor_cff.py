import FWCore.ParameterSet.Config as cms

hltMuonEfficiencies = cms.EDAnalyzer("DQMGenericClient",

    subDirs        = cms.untracked.vstring("HLT/Muon/Distributions.*"),
    verbose        = cms.untracked.uint32(0), # Set to 2 for all messages
    outputFileName = cms.untracked.string(''),
    commands       = cms.vstring(),
    resolution     = cms.vstring(),
    efficiency     = cms.vstring(
        "efficiencyPhiVsEta 'Efficiency to Match Reco Muons to Trigger Objects; #eta^{reco}; #phi^{reco}' efficiencyPhiVsEta_numer efficiencyPhiVsEta_denom",
    ),

    efficiencyProfile = cms.untracked.vstring(
        "efficiencyVertex 'Efficiency to Match Reco Muons to Trigger Objects; NVertex^{reco}; N(#mu matched to trigger object) / N(#mu)' efficiencyVertex_numer efficiencyVertex_denom",
        "efficiencyEta 'Efficiency to Match Reco Muons to Trigger Objects; #eta^{reco}; N(#mu matched to trigger object) / N(#mu)' efficiencyEta_numer efficiencyEta_denom",
        "efficiencyPhi 'Efficiency to Match Reco Muons to Trigger Objects; #phi^{reco}; N(#mu matched to trigger object) / N(#mu)' efficiencyPhi_numer efficiencyPhi_denom",
        "efficiencyTurnOn 'Efficiency to Match Reco Muons to Trigger Objects; p_{T}^{reco}; N(#mu matched to trigger object) / N(#mu)' efficiencyTurnOn_numer efficiencyTurnOn_denom",
        "efficiencyD0 'Efficiency to Match Reco Muons to Trigger Objects; d0^{reco}; N(#mu matched to trigger object) / N(#mu)' efficiencyD0_numer efficiencyD0_denom",
        "efficiencyZ0 'Efficiency to Match Reco Muons to Trigger Objects; z0^{reco}; N(#mu matched to trigger object) / N(#mu)' efficiencyZ0_numer efficiencyZ0_denom",
        "efficiencyCharge 'Efficiency to Match Reco Muons to Trigger Objects; q^{reco}; N(#mu matched to trigger object) / N(#mu)' efficiencyCharge_numer efficiencyCharge_denom",
        "fakerateVertex 'Trigger Fake Rate; NVertex^{trigger}; N(unmatched trigger objects) / N(trigger objects)' fakerateVertex_numer fakerateVertex_denom",
        "fakerateEta 'Trigger Fake Rate; #eta^{trigger}; N(unmatched trigger objects) / N(trigger objects)' fakerateEta_numer fakerateEta_denom",
        "fakeratePhi 'Trigger Fake Rate; #phi^{trigger}; N(unmatched trigger objects) / N(trigger objects)' fakeratePhi_numer fakeratePhi_denom",
        "fakerateTurnOn 'Trigger Fake Rate; p_{T}^{trigger}; N(unmatched trigger objects) / N(trigger objects)' fakerateTurnOn_numer fakerateTurnOn_denom",
        "TPefficiencyEtaJPsi 'Tag & Probe efficiency; #eta; N(tt) / N(tp)' massVsEtaJpsi_numer massVsEtaJpsi_denom",
        "TPefficiencyPtJPsi 'Tag & Probe efficiency; p_{T}; N(tt) / N(tp)' massVsPtJpsi_numer massVsPtJpsi_denom",
        "TPefficiencyVertexJPsi 'Tag & Probe efficiency; NVertex; N(tt) / N(tp)' massVsVertexJpsi_numer massVsVertexJpsi_denom",
        "TPefficiencyEtaZ 'Tag & Probe efficiency; #eta; N(tt) / N(tp)' massVsEtaZ_numer massVsEtaZ_denom",
        "TPefficiencyPtZ 'Tag & Probe efficiency; p_{T}; N(tt) / N(tp)' massVsPtZ_numer massVsPtZ_denom",
        "TPefficiencyVertexZ 'Tag & Probe efficiency; NVertex; N(tt) / N(tp)' massVsVertexZ_numer massVsVertexZ_denom",
        "Refefficiency_Eta_Mu1 'Reference efficiency; Eta; N(pass) / N' Refefficiency_Eta_Mu1_numer Refefficiency_Eta_Mu1_denom",
        "Refefficiency_Eta_Mu2 'Reference efficiency; Eta; N(pass) / N' Refefficiency_Eta_Mu2_numer Refefficiency_Eta_Mu2_denom",
        "Refefficiency_TurnOn_Mu1 'Reference efficiency; Pt; N(pass) / N' Refefficiency_TurnOn_Mu1_numer Refefficiency_TurnOn_Mu1_denom",
        "Refefficiency_TurnOn_Mu2 'Reference efficiency; Pt; N(pass) / N' Refefficiency_TurnOn_Mu2_numer Refefficiency_TurnOn_Mu2_denom",
        "Refefficiency_Vertex 'Reference efficiency; NVertex; N(pass) / N' Refefficiency_Vertex_numer Refefficiency_Vertex_denom",
        
    ),

)

hltMuonRefEfficiencies = cms.EDAnalyzer("HLTMuonRefMethod",
                                        subDirs        = cms.untracked.vstring("HLT/Muon/Distributions.*"),
                                        outputFileName = cms.untracked.string(''),
                                        hltTriggers    = cms.untracked.vstring("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ",
                                                                               "HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ"),
                                        refTriggers    = cms.untracked.string("HLT_Mu17_TrkIsoVVL"),
                                        efficiency     = cms.untracked.vstring( "Refefficiency_Eta_Mu1",
                                                                                "Refefficiency_Eta_Mu2",
                                                                                "Refefficiency_TurnOn_Mu1",
                                                                                "Refefficiency_TurnOn_Mu2",
                                                                                ),
                                        refEff         = cms.untracked.vstring( 'TPefficiencyEtaZ',
                                                                                'TPefficiencyEtaZ',
                                                                                'TPefficiencyPtZ', 
                                                                                'TPefficiencyPtZ'
                                                                                ),
                                        
                                        )
                                        


hltMuonPostVal = cms.Sequence(
    hltMuonEfficiencies*
    hltMuonRefEfficiencies
)





