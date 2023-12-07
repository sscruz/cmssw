import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoAOD.nano_eras_cff import *
from PhysicsTools.NanoAOD.common_cff import *
from PhysicsTools.NanoAOD.simpleCandidateFlatTableProducer_cfi import simpleCandidateFlatTableProducer

import PhysicsTools.PatAlgos.producersLayer1.muonProducer_cfi

# this below is used only in some eras
slimmedMuonsUpdated = cms.EDProducer("PATMuonUpdater",
    src = cms.InputTag("slimmedMuons"),
    vertices = cms.InputTag("offlineSlimmedPrimaryVertices"),
    computeMiniIso = cms.bool(False),
    fixDxySign = cms.bool(True),
    pfCandsForMiniIso = cms.InputTag("packedPFCandidates"),
    miniIsoParams = PhysicsTools.PatAlgos.producersLayer1.muonProducer_cfi.patMuons.miniIsoParams, # so they're in sync
    recomputeMuonBasicSelectors = cms.bool(False),
)

isoForMu = cms.EDProducer("MuonIsoValueMapProducer",
    src = cms.InputTag("slimmedMuonsUpdated"),
    relative = cms.bool(False),
    rho_MiniIso = cms.InputTag("fixedGridRhoFastjetAll"),
    EAFile_MiniIso = cms.FileInPath("PhysicsTools/NanoAOD/data/effAreaMuons_cone03_pfNeuHadronsAndPhotons_94X.txt"),
)

ptRatioRelForMu = cms.EDProducer("MuonJetVarProducer",
    srcJet = cms.InputTag("updatedJetsPuppi"),
    srcLep = cms.InputTag("slimmedMuonsUpdated"),
    srcVtx = cms.InputTag("offlineSlimmedPrimaryVertices"),
)

muonMVAID = cms.EDProducer("EvaluateMuonMVAID",
    src = cms.InputTag("slimmedMuonsUpdated"),
    weightFile =  cms.FileInPath("PhysicsTools/PatAlgos/data/rf67_zipmapNone.onnx"),
    isClassifier = cms.bool(False),
    backend = cms.string('ONNX'),
    name = cms.string("muonMVAID"),
    outputTensorName= cms.string("probabilities"),
    inputTensorName= cms.string("float_input"),
    outputNames = cms.vstring(["probGOOD", "wpMedium", "wpTight"]),
    batch_eval =cms.bool(True),
    outputFormulas = cms.vstring(["at(1)", "? at(1) > 0.14 ? 1 : 0", "? at(1) > 0.35 ? 1 : 0"]),
    variablesOrder = cms.vstring(["LepGood_global_muon","LepGood_validFraction","Muon_norm_chi2_extended","LepGood_local_chi2","LepGood_kink","LepGood_segmentComp","Muon_n_Valid_hits_extended","LepGood_n_MatchedStations","LepGood_Valid_pixel","LepGood_tracker_layers","LepGood_pt","LepGood_eta"]),
    variables = cms.PSet(
        LepGood_global_muon = cms.string("isGlobalMuon"),
        LepGood_validFraction = cms.string("?innerTrack.isNonnull?innerTrack().validFraction:-99"),
        LepGood_local_chi2 = cms.string("combinedQuality().chi2LocalPosition"),
        LepGood_kink = cms.string("combinedQuality().trkKink"),
        LepGood_segmentComp = cms.string("segmentCompatibility"),
        LepGood_n_MatchedStations = cms.string("numberOfMatchedStations()"),
        LepGood_Valid_pixel = cms.string("?innerTrack.isNonnull()?innerTrack().hitPattern().numberOfValidPixelHits():-99"),
        LepGood_tracker_layers = cms.string("?innerTrack.isNonnull()?innerTrack().hitPattern().trackerLayersWithMeasurement():-99"),
        LepGood_pt = cms.string("pt"),
        LepGood_eta = cms.string("eta"),
    ) 
)

slimmedMuonsWithUserData = cms.EDProducer("PATMuonUserDataEmbedder",
     src = cms.InputTag("slimmedMuonsUpdated"),
     userFloats = cms.PSet(
        miniIsoChg = cms.InputTag("isoForMu:miniIsoChg"),
        miniIsoAll = cms.InputTag("isoForMu:miniIsoAll"),
        ptRatio = cms.InputTag("ptRatioRelForMu:ptRatio"),
        ptRel = cms.InputTag("ptRatioRelForMu:ptRel"),
        jetNDauChargedMVASel = cms.InputTag("ptRatioRelForMu:jetNDauChargedMVASel"),
        mvaIDMuon_wpMedium = cms.InputTag("muonMVAID:wpMedium"),
        mvaIDMuon_wpTight = cms.InputTag("muonMVAID:wpTight"),
         mvaIDMuon = cms.InputTag("muonMVAID:probGOOD"),
     ),
     userCands = cms.PSet(
        jetForLepJetVar = cms.InputTag("ptRatioRelForMu:jetForLepJetVar") # warning: Ptr is null if no match is found
     ),
)


finalMuons = cms.EDFilter("PATMuonRefSelector",
    src = cms.InputTag("slimmedMuonsWithUserData"),
    cut = cms.string("pt > 15 || (pt > 3 && (passed('CutBasedIdLoose') || passed('SoftCutBasedId') || passed('SoftMvaId') || passed('CutBasedIdGlobalHighPt') || passed('CutBasedIdTrkHighPt')))")
)

finalLooseMuons = cms.EDFilter("PATMuonRefSelector", # for isotrack cleaning
    src = cms.InputTag("slimmedMuonsWithUserData"),
    cut = cms.string("pt > 3 && track.isNonnull && isLooseMuon")
)

                 
muonMVATTH= cms.EDProducer("MuonBaseMVAValueMapProducer",
    src = cms.InputTag("linkedObjects","muons"),
    weightFile =  cms.FileInPath("PhysicsTools/NanoAOD/data/mu_BDTG_2017.weights.xml"),
    name = cms.string("muonMVATTH"),
    isClassifier = cms.bool(True),
    variablesOrder = cms.vstring(["LepGood_pt","LepGood_eta","LepGood_jetNDauChargedMVASel","LepGood_miniRelIsoCharged","LepGood_miniRelIsoNeutral","LepGood_jetPtRelv2","LepGood_jetDF","LepGood_jetPtRatio","LepGood_dxy","LepGood_sip3d","LepGood_dz","LepGood_segmentComp"]),
    variables = cms.PSet(
        LepGood_pt = cms.string("pt"),
        LepGood_eta = cms.string("eta"),
        LepGood_jetNDauChargedMVASel = cms.string("?userCand('jetForLepJetVar').isNonnull()?userFloat('jetNDauChargedMVASel'):0"),
        LepGood_miniRelIsoCharged = cms.string("userFloat('miniIsoChg')/pt"),
        LepGood_miniRelIsoNeutral = cms.string("(userFloat('miniIsoAll')-userFloat('miniIsoChg'))/pt"),
        LepGood_jetPtRelv2 = cms.string("?userCand('jetForLepJetVar').isNonnull()?userFloat('ptRel'):0"),
        LepGood_jetDF = cms.string("?userCand('jetForLepJetVar').isNonnull()?max(userCand('jetForLepJetVar').bDiscriminator('pfDeepFlavourJetTags:probbb')+userCand('jetForLepJetVar').bDiscriminator('pfDeepFlavourJetTags:probb')+userCand('jetForLepJetVar').bDiscriminator('pfDeepFlavourJetTags:problepb'),0.0):0.0"),
        LepGood_jetPtRatio = cms.string("?userCand('jetForLepJetVar').isNonnull()?min(userFloat('ptRatio'),1.5):1.0/(1.0+(pfIsolationR04().sumChargedHadronPt + max(pfIsolationR04().sumNeutralHadronEt + pfIsolationR04().sumPhotonEt - pfIsolationR04().sumPUPt/2,0.0))/pt)"),
        LepGood_dxy = cms.string("log(abs(dB('PV2D')))"),
        LepGood_sip3d = cms.string("abs(dB('PV3D')/edB('PV3D'))"),
        LepGood_dz = cms.string("log(abs(dB('PVDZ')))"),
        LepGood_segmentComp = cms.string("segmentCompatibility"),

    )
)

muonMVALowPt = muonMVATTH.clone(
    weightFile =  cms.FileInPath("PhysicsTools/NanoAOD/data/mu_BDTG_lowpt.weights.xml"),
    name = cms.string("muonMVALowPt"),
)

run2_muon_2016.toModify(
    muonMVATTH,
    weightFile = "PhysicsTools/NanoAOD/data/mu_BDTG_2016.weights.xml",
)


pnetMuonVariables = cms.EDProducer("MuonInfoCollectionProducer",
                                   src = cms.InputTag("linkedObjects","muons"),
                                   secondary_vertices=cms.InputTag("slimmedSecondaryVertices"),
                                   pvSrc = cms.InputTag("offlineSlimmedPrimaryVertices"),
                                   pfCandidates=cms.InputTag("packedPFCandidates"),
                                   leptonVars = cms.PSet(
                                       MuonSelected_LepGood_pt = cms.string("pt"),
                                       MuonSelected_LepGood_eta = cms.string("eta"),
                                       MuonSelected_LepGood_jetNDauChargedMVASel = cms.string("?userCand('jetForLepJetVar').isNonnull()?userFloat('jetNDauChargedMVASel'):0"),
                                       MuonSelected_LepGood_miniRelIsoCharged = cms.string("userFloat('miniIsoChg')/pt"),
                                       MuonSelected_LepGood_miniRelIsoNeutral = cms.string("(userFloat('miniIsoAll')-userFloat('miniIsoChg'))/pt"),
                                       MuonSelected_LepGood_jetPtRelv2 = cms.string("?userCand('jetForLepJetVar').isNonnull()?userFloat('ptRel'):0"),
                                       MuonSelected_LepGood_jetDF = cms.string("?userCand('jetForLepJetVar').isNonnull()?max(userCand('jetForLepJetVar').bDiscriminator('pfDeepFlavourJetTags:probbb')+userCand('jetForLepJetVar').bDiscriminator('pfDeepFlavourJetTags:probb')+userCand('jetForLepJetVar').bDiscriminator('pfDeepFlavourJetTags:problepb'),0.0):0.0"),
                                       MuonSelected_LepGood_jetPtRatio = cms.string("?userCand('jetForLepJetVar').isNonnull()?min(userFloat('ptRatio'),1.5):1.0/(1.0+(pfIsolationR04().sumChargedHadronPt + max(pfIsolationR04().sumNeutralHadronEt + pfIsolationR04().sumPhotonEt - pfIsolationR04().sumPUPt/2,0.0))/pt)"),
                                       MuonSelected_dxy = cms.string("log(abs(dB('PV2D')))"),
                                       MuonSelected_sip3d = cms.string("abs(dB('PV3D')/edB('PV3D'))"),
                                       MuonSelected_dz = cms.string("log(abs(dB('PVDZ')))"),
                                       MuonSelected_LepGood_dz = cms.string("log(abs(dB('PVDZ')))"),
                                       MuonSelected_segmentComp = cms.string("segmentCompatibility"),
                                       MuonSelected_global_muon = cms.string("isGlobalMuon"),
                                       MuonSelected_validFraction = cms.string("?innerTrack.isNonnull?innerTrack().validFraction:-99"),
                                       MuonSelected_local_chi2 = cms.string("combinedQuality().chi2LocalPosition"),
                                       MuonSelected_kink = cms.string("combinedQuality().trkKink"),
                                       MuonSelected_n_MatchedStations = cms.string("numberOfMatchedStations()"),
                                       MuonSelected_Valid_pixel = cms.string("?innerTrack.isNonnull()?innerTrack().hitPattern().numberOfValidPixelHits():-99"),
                                       MuonSelected_tracker_layers = cms.string("?innerTrack.isNonnull()?innerTrack().hitPattern().trackerLayersWithMeasurement():-99"),
                                       MuonSelected_mvaId=cms.string("userFloat('mvaIDMuon')"),
                                   ),
                                   leptonVarsExt = cms.PSet(
                                       MuonSelected_mvaTTH=cms.InputTag("muonMVATTH"),
                                   ),
                                   pfVars = cms.PSet(
                                       PF_pt=cms.string("pt"),
                                       PF_charge=cms.string("charge"),
                                       PF_isElectron=cms.string("?abs(pdgId)==11?1:0"),
                                       PF_isMuon=cms.string("?abs(pdgId)==13?1:0"),
                                       PF_isNeutralHadron=cms.string("?abs(pdgId)==130?1:0"),
                                       PF_isPhoton=cms.string("?abs(pdgId)==22?1:0"),
                                       PF_isChargedHadron=cms.string("?abs(pdgId)==211?1:0"),
                                       PF_puppiWeightNoLep=cms.string("puppiWeightNoLep"),
                                       PF_fromPV=cms.string("fromPV"),
                                       PF_numberOfPixelHits=cms.string("numberOfPixelHits"),
                                       PF_dzSig=cms.string("?hasTrackDetails?dz/max(dzError,1.e-6):0"),
                                       PF_dxySig=cms.string("?hasTrackDetails?dxy/max(dxyError,1.e-6):0"),
                                       PF_hcalFraction=cms.string("hcalFraction"),
                                       PF_trackerLayersWithMeasurement=cms.string("?hasTrackDetails?bestTrack().hitPattern().trackerLayersWithMeasurement:0"),
                                       pf_mask=cms.string("1"),
                                   ),
                                   svVars = cms.PSet(
                                       SV_eta=cms.string("eta"),
                                       SV_phi=cms.string("phi"),
                                       SV_pt=cms.string("pt"),
                                       SV_ndof=cms.string("vertexNdof"),
                                       SV_chi2=cms.string("vertexChi2"),
                                       SV_nTracks=cms.string("numberOfDaughters"),
                                       SV_mass=cms.string("mass"),
                                       SV_mask=cms.string("1"),
                                   ),
)

muonTable = simpleCandidateFlatTableProducer.clone(
    src = cms.InputTag("linkedObjects","muons"),
    name = cms.string("Muon"),
    doc  = cms.string("slimmedMuons after basic selection (" + finalMuons.cut.value()+")"),
    variables = cms.PSet(CandVars,
        ptErr   = Var("bestTrack().ptError()", float, doc = "ptError of the muon track", precision=6),
        tunepRelPt = Var("tunePMuonBestTrack().pt/pt",float,doc="TuneP relative pt, tunePpt/pt",precision=6),
        dz = Var("dB('PVDZ')",float,doc="dz (with sign) wrt first PV, in cm",precision=10),
        dzErr = Var("abs(edB('PVDZ'))",float,doc="dz uncertainty, in cm",precision=6),
        dxybs = Var("dB('BS2D')",float,doc="dxy (with sign) wrt the beam spot, in cm",precision=10),
        dxy = Var("dB('PV2D')",float,doc="dxy (with sign) wrt first PV, in cm",precision=10),
        dxyErr = Var("edB('PV2D')",float,doc="dxy uncertainty, in cm",precision=6),
        ip3d = Var("abs(dB('PV3D'))",float,doc="3D impact parameter wrt first PV, in cm",precision=10),
        sip3d = Var("abs(dB('PV3D')/edB('PV3D'))",float,doc="3D impact parameter significance wrt first PV",precision=10),
        segmentComp   = Var("segmentCompatibility()", float, doc = "muon segment compatibility", precision=14), # keep higher precision since people have cuts with 3 digits on this
        nStations = Var("numberOfMatchedStations", int, doc = "number of matched stations with default arbitration (segment & track)"),
        nTrackerLayers = Var("?track.isNonnull?innerTrack().hitPattern().trackerLayersWithMeasurement():0", int, doc = "number of layers in the tracker"),
        highPurity = Var("?track.isNonnull?innerTrack().quality('highPurity'):0", bool, doc = "inner track is high purity"),
        jetIdx = Var("?hasUserCand('jet')?userCand('jet').key():-1", int, doc="index of the associated jet (-1 if none)"),
        svIdx = Var("?hasUserCand('vertex')?userCand('vertex').key():-1", int, doc="index of matching secondary vertex"),
        tkRelIso = Var("isolationR03().sumPt/tunePMuonBestTrack().pt",float,doc="Tracker-based relative isolation dR=0.3 for highPt, trkIso/tunePpt",precision=6),
        miniPFRelIso_chg = Var("userFloat('miniIsoChg')/pt",float,doc="mini PF relative isolation, charged component"),
        miniPFRelIso_all = Var("userFloat('miniIsoAll')/pt",float,doc="mini PF relative isolation, total (with scaled rho*EA PU corrections)"),
        pfRelIso03_chg = Var("pfIsolationR03().sumChargedHadronPt/pt",float,doc="PF relative isolation dR=0.3, charged component"),
        pfRelIso03_all = Var("(pfIsolationR03().sumChargedHadronPt + max(pfIsolationR03().sumNeutralHadronEt + pfIsolationR03().sumPhotonEt - pfIsolationR03().sumPUPt/2,0.0))/pt",float,doc="PF relative isolation dR=0.3, total (deltaBeta corrections)"),
        pfRelIso04_all = Var("(pfIsolationR04().sumChargedHadronPt + max(pfIsolationR04().sumNeutralHadronEt + pfIsolationR04().sumPhotonEt - pfIsolationR04().sumPUPt/2,0.0))/pt",float,doc="PF relative isolation dR=0.4, total (deltaBeta corrections)"),
        jetRelIso = Var("?userCand('jetForLepJetVar').isNonnull()?(1./userFloat('ptRatio'))-1.:(pfIsolationR04().sumChargedHadronPt + max(pfIsolationR04().sumNeutralHadronEt + pfIsolationR04().sumPhotonEt - pfIsolationR04().sumPUPt/2,0.0))/pt",float,doc="Relative isolation in matched jet (1/ptRatio-1, pfRelIso04_all if no matched jet)",precision=8),
        jetPtRelv2 = Var("?userCand('jetForLepJetVar').isNonnull()?userFloat('ptRel'):0",float,doc="Relative momentum of the lepton with respect to the closest jet after subtracting the lepton",precision=8),
        tightCharge = Var("?(muonBestTrack().ptError()/muonBestTrack().pt() < 0.2)?2:0",int,doc="Tight charge criterion using pterr/pt of muonBestTrack (0:fail, 2:pass)"),
        looseId  = Var("passed('CutBasedIdLoose')",bool, doc="muon is loose muon"),
        isPFcand = Var("isPFMuon",bool,doc="muon is PF candidate"),
        isGlobal = Var("isGlobalMuon",bool,doc="muon is global muon"),
        isTracker = Var("isTrackerMuon",bool,doc="muon is tracker muon"),
        isStandalone = Var("isStandAloneMuon",bool,doc="muon is a standalone muon"),
        mediumId = Var("passed('CutBasedIdMedium')",bool,doc="cut-based ID, medium WP"),
        mediumPromptId = Var("passed('CutBasedIdMediumPrompt')",bool,doc="cut-based ID, medium prompt WP"),
        tightId = Var("passed('CutBasedIdTight')",bool,doc="cut-based ID, tight WP"),
        softId = Var("passed('SoftCutBasedId')",bool,doc="soft cut-based ID"),
        softMvaId = Var("passed('SoftMvaId')",bool,doc="soft MVA ID"),
        softMva = Var("softMvaValue()",float,doc="soft MVA ID score",precision=6),
        highPtId = Var("?passed('CutBasedIdGlobalHighPt')?2:passed('CutBasedIdTrkHighPt')","uint8",doc="high-pT cut-based ID (1 = tracker high pT, 2 = global high pT, which includes tracker high pT)"),
        pfIsoId = Var("passed('PFIsoVeryLoose')+passed('PFIsoLoose')+passed('PFIsoMedium')+passed('PFIsoTight')+passed('PFIsoVeryTight')+passed('PFIsoVeryVeryTight')","uint8",doc="PFIso ID from miniAOD selector (1=PFIsoVeryLoose, 2=PFIsoLoose, 3=PFIsoMedium, 4=PFIsoTight, 5=PFIsoVeryTight, 6=PFIsoVeryVeryTight)"),
        tkIsoId = Var("?passed('TkIsoTight')?2:passed('TkIsoLoose')","uint8",doc="TkIso ID (1=TkIsoLoose, 2=TkIsoTight)"),
        mvaId = Var("passed('MvaLoose')+passed('MvaMedium')+passed('MvaTight')+passed('MvaVTight')+passed('MvaVVTight')","uint8",doc="Mva for ID of prompt leptons from miniAOD selector (1=MvaLoose, 2=MvaMedium, 3=MvaTight, 4=MvaVTight, 5=MvaVVTight)"),
        mvaLowPtId = Var("passed('LowPtMvaLoose')+passed('LowPtMvaMedium')","uint8", doc="Low Pt Mva ID from miniAOD selector (1=LowPtMvaLoose, 2=LowPtMvaMedium)"),
        miniIsoId = Var("passed('MiniIsoLoose')+passed('MiniIsoMedium')+passed('MiniIsoTight')+passed('MiniIsoVeryTight')","uint8",doc="MiniIso ID from miniAOD selector (1=MiniIsoLoose, 2=MiniIsoMedium, 3=MiniIsoTight, 4=MiniIsoVeryTight)"),
        mvaMuID = Var("mvaIDValue()",float,doc="MVA-based ID score ",precision=6),
        mvaMuID_WP = Var("userFloat('mvaIDMuon_wpMedium') + userFloat('mvaIDMuon_wpTight')","uint8",doc="MVA-based ID selector WPs (1=MVAIDwpMedium,2=MVAIDwpTight)"),
        multiIsoId = Var("?passed('MultiIsoMedium')?2:passed('MultiIsoLoose')","uint8",doc="MultiIsoId from miniAOD selector (1=MultiIsoLoose, 2=MultiIsoMedium)"),
        puppiIsoId = Var("passed('PuppiIsoLoose')+passed('PuppiIsoMedium')+passed('PuppiIsoTight')", "uint8", doc="PuppiIsoId from miniAOD selector (1=Loose, 2=Medium, 3=Tight)"),
        triggerIdLoose = Var("passed('TriggerIdLoose')",bool,doc="TriggerIdLoose ID"),
        inTimeMuon = Var("passed('InTimeMuon')",bool,doc="inTimeMuon ID"),
        jetNDauCharged = Var("?userCand('jetForLepJetVar').isNonnull()?userFloat('jetNDauChargedMVASel'):0", "uint8", doc="number of charged daughters of the closest jet"),
        ),
    externalVariables = cms.PSet(
        mvaTTH = ExtVar(cms.InputTag("muonMVATTH"),float, doc="TTH MVA lepton ID score",precision=14),
        mvaLowPt = ExtVar(cms.InputTag("muonMVALowPt"),float, doc="Low pt muon ID score",precision=14),

        pnScore_1_light = ExtVar(cms.InputTag("muonPNjun28norw202308151202091:pnScorelight"),float, doc="Score of PN muon id",precision=14),
        pnScore_1_prompt = ExtVar(cms.InputTag("muonPNjun28norw202308151202091:pnScoreprompt"),float, doc="Score of PN muon id",precision=14),
        pnScore_1_heavy = ExtVar(cms.InputTag("muonPNjun28norw202308151202091:pnScoreheavy"),float, doc="Score of PN muon id",precision=14),

        pnScore_2_light = ExtVar(cms.InputTag("muonPNjun28norw202308151202092:pnScorelight"),float, doc="Score of PN muon id",precision=14),
        pnScore_2_prompt = ExtVar(cms.InputTag("muonPNjun28norw202308151202092:pnScoreprompt"),float, doc="Score of PN muon id",precision=14),
        pnScore_2_heavy = ExtVar(cms.InputTag("muonPNjun28norw202308151202092:pnScoreheavy"),float, doc="Score of PN muon id",precision=14),

        pnScore_3_light = ExtVar(cms.InputTag("muonPNjun28202308151202091:pnScorelight"),float, doc="Score of PN muon id",precision=14),
        pnScore_3_prompt = ExtVar(cms.InputTag("muonPNjun28202308151202091:pnScoreprompt"),float, doc="Score of PN muon id",precision=14),
        pnScore_3_heavy = ExtVar(cms.InputTag("muonPNjun28202308151202091:pnScoreheavy"),float, doc="Score of PN muon id",precision=14),

        pnScore_4_light = ExtVar(cms.InputTag("muonPNjun28202308151202092:pnScorelight"),float, doc="Score of PN muon id",precision=14),
        pnScore_4_prompt = ExtVar(cms.InputTag("muonPNjun28202308151202092:pnScoreprompt"),float, doc="Score of PN muon id",precision=14),
        pnScore_4_heavy = ExtVar(cms.InputTag("muonPNjun28202308151202092:pnScoreheavy"),float, doc="Score of PN muon id",precision=14),

        pnScore_5_prompt = ExtVar(cms.InputTag("muonPNjun28noclasses202308151202091:pnScoreprompt"),float, doc="Score of PN muon id",precision=14),
        pnScore_5_nonprompt = ExtVar(cms.InputTag("muonPNjun28noclasses202308151202091:pnScorenonprompt"),float, doc="Score of PN muon id",precision=14),

        pnScore_6_prompt = ExtVar(cms.InputTag("muonPNjun28noclasses202308151202092:pnScoreprompt"),float, doc="Score of PN muon id",precision=14),
        pnScore_6_nonprompt = ExtVar(cms.InputTag("muonPNjun28noclasses202308151202092:pnScorenonprompt"),float, doc="Score of PN muon id",precision=14),

        pnScore_7_light = ExtVar(cms.InputTag("muonPNjun28norwwithtaus1:pnScorelight"),float, doc="Score of PN muon id",precision=14),
        pnScore_7_prompt = ExtVar(cms.InputTag("muonPNjun28norwwithtaus1:pnScoreprompt"),float, doc="Score of PN muon id",precision=14),
        pnScore_7_heavy = ExtVar(cms.InputTag("muonPNjun28norwwithtaus1:pnScoreheavy"),float, doc="Score of PN muon id",precision=14),
        pnScore_7_tau   = ExtVar(cms.InputTag("muonPNjun28norwwithtaus1:pnScoretau"),float, doc="Score of PN muon id",precision=14),

        pnScore_8_light = ExtVar(cms.InputTag("muonPNjun28norwwithtaus2:pnScorelight"),float, doc="Score of PN muon id",precision=14),
        pnScore_8_prompt = ExtVar(cms.InputTag("muonPNjun28norwwithtaus2:pnScoreprompt"),float, doc="Score of PN muon id",precision=14),
        pnScore_8_heavy = ExtVar(cms.InputTag("muonPNjun28norwwithtaus2:pnScoreheavy"),float, doc="Score of PN muon id",precision=14),
        pnScore_8_tau   = ExtVar(cms.InputTag("muonPNjun28norwwithtaus2:pnScoretau"),float, doc="Score of PN muon id",precision=14),

        pnScore_9_light = ExtVar(cms.InputTag("muonPNjun28withtaus1:pnScorelight"),float, doc="Score of PN muon id",precision=14),
        pnScore_9_prompt = ExtVar(cms.InputTag("muonPNjun28withtaus1:pnScoreprompt"),float, doc="Score of PN muon id",precision=14),
        pnScore_9_heavy = ExtVar(cms.InputTag("muonPNjun28withtaus1:pnScoreheavy"),float, doc="Score of PN muon id",precision=14),
        pnScore_9_tau   = ExtVar(cms.InputTag("muonPNjun28withtaus1:pnScoretau"),float, doc="Score of PN muon id",precision=14),

        pnScore_10_light = ExtVar(cms.InputTag("muonPNjun28withtaus2:pnScorelight"),float, doc="Score of PN muon id",precision=14),
        pnScore_10_prompt = ExtVar(cms.InputTag("muonPNjun28withtaus2:pnScoreprompt"),float, doc="Score of PN muon id",precision=14),
        pnScore_10_heavy = ExtVar(cms.InputTag("muonPNjun28withtaus2:pnScoreheavy"),float, doc="Score of PN muon id",precision=14),
        pnScore_10_tau   = ExtVar(cms.InputTag("muonPNjun28withtaus2:pnScoretau"),float, doc="Score of PN muon id",precision=14),

        pnScore_v2_rw1_light = ExtVar(cms.InputTag("muonPNv2rw1:pnScorelight"),float, doc="Score of PN muon id",precision=14),
        pnScore_v2_rw1_prompt = ExtVar(cms.InputTag("muonPNv2rw1:pnScoreprompt"),float, doc="Score of PN muon id",precision=14),
        pnScore_v2_rw1_heavy = ExtVar(cms.InputTag("muonPNv2rw1:pnScoreheavy"),float, doc="Score of PN muon id",precision=14),
        pnScore_v2_rw1_tau   = ExtVar(cms.InputTag("muonPNv2rw1:pnScoretau"),float, doc="Score of PN muon id",precision=14),

        pnScore_v2_rw2_light = ExtVar(cms.InputTag("muonPNv2rw2:pnScorelight"),float, doc="Score of PN muon id",precision=14),
        pnScore_v2_rw2_prompt = ExtVar(cms.InputTag("muonPNv2rw2:pnScoreprompt"),float, doc="Score of PN muon id",precision=14),
        pnScore_v2_rw2_heavy = ExtVar(cms.InputTag("muonPNv2rw2:pnScoreheavy"),float, doc="Score of PN muon id",precision=14),
        pnScore_v2_rw2_tau   = ExtVar(cms.InputTag("muonPNv2rw2:pnScoretau"),float, doc="Score of PN muon id",precision=14),

        pnScore_v2_norw1_light = ExtVar(cms.InputTag("muonPNv2norw1:pnScorelight"),float, doc="Score of PN muon id",precision=14),
        pnScore_v2_norw1_prompt = ExtVar(cms.InputTag("muonPNv2norw1:pnScoreprompt"),float, doc="Score of PN muon id",precision=14),
        pnScore_v2_norw1_heavy = ExtVar(cms.InputTag("muonPNv2norw1:pnScoreheavy"),float, doc="Score of PN muon id",precision=14),
        pnScore_v2_norw1_tau   = ExtVar(cms.InputTag("muonPNv2norw1:pnScoretau"),float, doc="Score of PN muon id",precision=14),

        pnScore_v2_norw2_light = ExtVar(cms.InputTag("muonPNv2norw2:pnScorelight"),float, doc="Score of PN muon id",precision=14),
        pnScore_v2_norw2_prompt = ExtVar(cms.InputTag("muonPNv2norw2:pnScoreprompt"),float, doc="Score of PN muon id",precision=14),
        pnScore_v2_norw2_heavy = ExtVar(cms.InputTag("muonPNv2norw2:pnScoreheavy"),float, doc="Score of PN muon id",precision=14),
        pnScore_v2_norw2_tau   = ExtVar(cms.InputTag("muonPNv2norw2:pnScoretau"),float, doc="Score of PN muon id",precision=14),


        fsrPhotonIdx = ExtVar(cms.InputTag("leptonFSRphotons:muFsrIndex"),int, doc="Index of the lowest-dR/ET2 among associated FSR photons"),
    ),
)

muonPNjun28norw202308151202091 = cms.EDProducer('PNETMuonProducer',
                        src = cms.InputTag("pnetMuonVariables"),
                        srcLeps = cms.InputTag("linkedObjects","muons"),
                        model_path=cms.FileInPath('PhysicsTools/PatAlgos/data/jun28_norw_20230815-120209_particlenet_pf_sv_withhighlevel_ranger_lr0.0005_batch128/model.onnx'),
                        preprocess_json=cms.string('PhysicsTools/PatAlgos/data/jun28_norw_20230815-120209_particlenet_pf_sv_withhighlevel_ranger_lr0.0005_batch128/preprocess.json'),
                        name=cms.string("PN_lepton"),
                        debugMode=cms.untracked.bool(True),
                        flav_names = cms.vstring(["light","prompt","heavy"]),
)
muonPNjun28norw202308151202092 = cms.EDProducer('PNETMuonProducer',
                        src = cms.InputTag("pnetMuonVariables"),
                        srcLeps = cms.InputTag("linkedObjects","muons"),
                        model_path=cms.FileInPath('PhysicsTools/PatAlgos/data/jun28_norw_20230815-120209_particlenet_pf_sv_withhighlevel_ranger_lr0.005_batch128/model.onnx'),
                        preprocess_json=cms.string('PhysicsTools/PatAlgos/data/jun28_norw_20230815-120209_particlenet_pf_sv_withhighlevel_ranger_lr0.005_batch128/preprocess.json'),
                        name=cms.string("PN_lepton"),
                        debugMode=cms.untracked.bool(True),
                        flav_names = cms.vstring(["light","prompt","heavy"]),
)


muonPNjun28202308151202091 = cms.EDProducer('PNETMuonProducer',
                        src = cms.InputTag("pnetMuonVariables"),
                        srcLeps = cms.InputTag("linkedObjects","muons"),
                        model_path=cms.FileInPath('PhysicsTools/PatAlgos/data/jun28_rw_20230815-120209_particlenet_pf_sv_withhighlevel_ranger_lr0.0005_batch128/model.onnx'),
                        preprocess_json=cms.string('PhysicsTools/PatAlgos/data/jun28_rw_20230815-120209_particlenet_pf_sv_withhighlevel_ranger_lr0.0005_batch128/preprocess.json'),
                        name=cms.string("PN_lepton"),
                        debugMode=cms.untracked.bool(True),
                        flav_names = cms.vstring(["light","prompt","heavy"]),
)
muonPNjun28202308151202092 = cms.EDProducer('PNETMuonProducer',
                        src = cms.InputTag("pnetMuonVariables"),
                        srcLeps = cms.InputTag("linkedObjects","muons"),
                        model_path=cms.FileInPath('PhysicsTools/PatAlgos/data/jun28_rw_20230815-120209_particlenet_pf_sv_withhighlevel_ranger_lr0.005_batch128/model.onnx'),
                        preprocess_json=cms.string('PhysicsTools/PatAlgos/data/jun28_rw_20230815-120209_particlenet_pf_sv_withhighlevel_ranger_lr0.005_batch128/preprocess.json'),
                        name=cms.string("PN_lepton"),
                        debugMode=cms.untracked.bool(True),
                        flav_names = cms.vstring(["light","prompt","heavy"]),
)

muonPNjun28noclasses202308151202091 = cms.EDProducer('PNETMuonProducer',
                        src = cms.InputTag("pnetMuonVariables"),
                        srcLeps = cms.InputTag("linkedObjects","muons"),
                        model_path=cms.FileInPath('PhysicsTools/PatAlgos/data/jun28_norw_noclasses_20230815-120209_particlenet_pf_sv_withhighlevel_ranger_lr0.0005_batch128/model.onnx'),
                        preprocess_json=cms.string('PhysicsTools/PatAlgos/data/jun28_norw_noclasses_20230815-120209_particlenet_pf_sv_withhighlevel_ranger_lr0.0005_batch128/preprocess.json'),
                        name=cms.string("PN_lepton"),
                        debugMode=cms.untracked.bool(True),
                        flav_names = cms.vstring(["prompt","nonprompt"]),
)
muonPNjun28noclasses202308151202092 = cms.EDProducer('PNETMuonProducer',
                        src = cms.InputTag("pnetMuonVariables"),
                        srcLeps = cms.InputTag("linkedObjects","muons"),
                        model_path=cms.FileInPath('PhysicsTools/PatAlgos/data/jun28_norw_noclasses_20230815-120209_particlenet_pf_sv_withhighlevel_ranger_lr0.005_batch128/model.onnx'),
                        preprocess_json=cms.string('PhysicsTools/PatAlgos/data/jun28_norw_noclasses_20230815-120209_particlenet_pf_sv_withhighlevel_ranger_lr0.005_batch128/preprocess.json'),
                        name=cms.string("PN_lepton"),
                        debugMode=cms.untracked.bool(True),
                        flav_names = cms.vstring(["prompt","nonprompt"]),
)

muonPNjun28withtaus1 = cms.EDProducer('PNETMuonProducer',
                        src = cms.InputTag("pnetMuonVariables"),
                        srcLeps = cms.InputTag("linkedObjects","muons"),
                        model_path=cms.FileInPath('PhysicsTools/PatAlgos/data/jun28_withtaus_20230912-100919_particlenet_pf_sv_withhighlevel_ranger_lr0.0001_batch128/model.onnx'),
                        preprocess_json=cms.string('PhysicsTools/PatAlgos/data/jun28_withtaus_20230912-100919_particlenet_pf_sv_withhighlevel_ranger_lr0.0001_batch128/preprocess.json'),
                        name=cms.string("PN_lepton"),
                        debugMode=cms.untracked.bool(True),
                        flav_names = cms.vstring(["light","prompt","tau","heavy"]),
)
muonPNjun28withtaus2 = cms.EDProducer('PNETMuonProducer',
                        src = cms.InputTag("pnetMuonVariables"),
                        srcLeps = cms.InputTag("linkedObjects","muons"),
                        model_path=cms.FileInPath('PhysicsTools/PatAlgos/data/jun28_withtaus_20230912-100919_particlenet_pf_sv_withhighlevel_ranger_lr0.0005_batch128/model.onnx'),
                        preprocess_json=cms.string('PhysicsTools/PatAlgos/data/jun28_withtaus_20230912-100919_particlenet_pf_sv_withhighlevel_ranger_lr0.0005_batch128/preprocess.json'),
                        name=cms.string("PN_lepton"),
                        debugMode=cms.untracked.bool(True),
                        flav_names = cms.vstring(["light","prompt","tau","heavy"]),
)

muonPNjun28norwwithtaus1 = cms.EDProducer('PNETMuonProducer',
                        src = cms.InputTag("pnetMuonVariables"),
                        srcLeps = cms.InputTag("linkedObjects","muons"),
                        model_path=cms.FileInPath('PhysicsTools/PatAlgos/data/jun28_norw_withtaus_20230912-100919_particlenet_pf_sv_withhighlevel_ranger_lr0.0001_batch128/model.onnx'),
                        preprocess_json=cms.string('PhysicsTools/PatAlgos/data/jun28_norw_withtaus_20230912-100919_particlenet_pf_sv_withhighlevel_ranger_lr0.0001_batch128/preprocess.json'),
                        name=cms.string("PN_lepton"),
                        debugMode=cms.untracked.bool(True),
                        flav_names = cms.vstring(["light","prompt","tau","heavy"]),
)
muonPNjun28norwwithtaus2 = cms.EDProducer('PNETMuonProducer',
                        src = cms.InputTag("pnetMuonVariables"),
                        srcLeps = cms.InputTag("linkedObjects","muons"),
                        model_path=cms.FileInPath('PhysicsTools/PatAlgos/data/jun28_norw_withtaus_20230912-100919_particlenet_pf_sv_withhighlevel_ranger_lr0.0005_batch128/model.onnx'),
                        preprocess_json=cms.string('PhysicsTools/PatAlgos/data/jun28_norw_withtaus_20230912-100919_particlenet_pf_sv_withhighlevel_ranger_lr0.0005_batch128/preprocess.json'),
                        name=cms.string("PN_lepton"),
                        debugMode=cms.untracked.bool(True),
                        flav_names = cms.vstring(["light","prompt","tau","heavy"]),
)

muonPNv2rw1 = cms.EDProducer('PNETMuonProducer',
                        src = cms.InputTag("pnetMuonVariables"),
                        srcLeps = cms.InputTag("linkedObjects","muons"),
                        model_path=cms.FileInPath('PhysicsTools/PatAlgos/data/sep27_withtaus_rw_20230929-172416_particlenet_pf_sv_withhighlevel_ranger_lr0.0005_batch128/model.onnx'),
                        preprocess_json=cms.string('PhysicsTools/PatAlgos/data/sep27_withtaus_rw_20230929-172416_particlenet_pf_sv_withhighlevel_ranger_lr0.0005_batch128/preprocess.json'),
                        name=cms.string("PN_lepton"),
                        debugMode=cms.untracked.bool(True),
                        flav_names = cms.vstring(["light","prompt","tau","heavy"]),
)
muonPNv2rw2 = cms.EDProducer('PNETMuonProducer',
                        src = cms.InputTag("pnetMuonVariables"),
                        srcLeps = cms.InputTag("linkedObjects","muons"),
                        model_path=cms.FileInPath('PhysicsTools/PatAlgos/data/sep27_withtaus_rw_20230929-181423_particlenet_pf_sv_withhighlevel_ranger_lr0.0001_batch128/model.onnx'),
                        preprocess_json=cms.string('PhysicsTools/PatAlgos/data/sep27_withtaus_rw_20230929-181423_particlenet_pf_sv_withhighlevel_ranger_lr0.0001_batch128/preprocess.json'),
                        name=cms.string("PN_lepton"),
                        debugMode=cms.untracked.bool(True),
                        flav_names = cms.vstring(["light","prompt","tau","heavy"]),
)

muonPNv2norw1 = cms.EDProducer('PNETMuonProducer',
                        src = cms.InputTag("pnetMuonVariables"),
                        srcLeps = cms.InputTag("linkedObjects","muons"),
                        model_path=cms.FileInPath('PhysicsTools/PatAlgos/data/sep27_withtaus_20230929-172416_particlenet_pf_sv_withhighlevel_ranger_lr0.0005_batch128/model.onnx'),
                        preprocess_json=cms.string('PhysicsTools/PatAlgos/data/sep27_withtaus_20230929-172416_particlenet_pf_sv_withhighlevel_ranger_lr0.0005_batch128/preprocess.json'),
                        name=cms.string("PN_lepton"),
                        debugMode=cms.untracked.bool(True),
                        flav_names = cms.vstring(["light","prompt","tau","heavy"]),
)
muonPNv2norw2 = cms.EDProducer('PNETMuonProducer',
                        src = cms.InputTag("pnetMuonVariables"),
                        srcLeps = cms.InputTag("linkedObjects","muons"),
                        model_path=cms.FileInPath('PhysicsTools/PatAlgos/data/sep27_withtaus_20231001-103150_particlenet_pf_sv_withhighlevel_ranger_lr0.0001_batch128/model.onnx'),
                        preprocess_json=cms.string('PhysicsTools/PatAlgos/data/sep27_withtaus_20231001-103150_particlenet_pf_sv_withhighlevel_ranger_lr0.0001_batch128/preprocess.json'),
                        name=cms.string("PN_lepton"),
                        debugMode=cms.untracked.bool(True),
                        flav_names = cms.vstring(["light","prompt","tau","heavy"]),
)

(run2_nanoAOD_106Xv2 | run3_nanoAOD_122).toModify(muonTable.variables,mvaMuID=None).toModify(
     muonTable.variables, mvaMuID = Var("userFloat('mvaIDMuon')", float, doc="MVA-based ID score",precision=6))


# Revert back to AK4 CHS jets for Run 2
run2_nanoAOD_ANY.toModify(
    ptRatioRelForMu,srcJet="updatedJets"
)


muonsMCMatchForTable = cms.EDProducer("MCMatcher",       # cut on deltaR, deltaPt/Pt; pick best by deltaR
    src         = muonTable.src,                         # final reco collection
    matched     = cms.InputTag("finalGenParticles"),     # final mc-truth particle collection
    mcPdgId     = cms.vint32(13),               # one or more PDG ID (13 = mu); absolute values (see below)
    checkCharge = cms.bool(False),              # True = require RECO and MC objects to have the same charge
    mcStatus    = cms.vint32(1),                # PYTHIA status code (1 = stable, 2 = shower, 3 = hard scattering)
    maxDeltaR   = cms.double(0.3),              # Minimum deltaR for the match
    maxDPtRel   = cms.double(0.5),              # Minimum deltaPt/Pt for the match
    resolveAmbiguities    = cms.bool(True),     # Forbid two RECO objects to match to the same GEN object
    resolveByMatchQuality = cms.bool(True),    # False = just match input in order; True = pick lowest deltaR pair first
)

muonMCTable = cms.EDProducer("CandMCMatchTableProducer",
    src     = muonTable.src,
    mcMap   = cms.InputTag("muonsMCMatchForTable"),
    objName = muonTable.name,
    objType = muonTable.name, #cms.string("Muon"),
    branchName = cms.string("genPart"),
    docString = cms.string("MC matching to status==1 muons"),
)

muonTask = cms.Task(slimmedMuonsUpdated,isoForMu,ptRatioRelForMu,slimmedMuonsWithUserData,finalMuons,finalLooseMuons )
muonMCTask = cms.Task(muonsMCMatchForTable,muonMCTable)
muonTablesTask = cms.Task(muonMVATTH,muonMVALowPt,muonMVAID,pnetMuonVariables,muonPNjun28norw202308151202091, muonPNjun28norw202308151202092,muonPNjun28202308151202091, muonPNjun28202308151202092, muonPNjun28noclasses202308151202091, muonPNjun28noclasses202308151202092, muonPNjun28withtaus1,muonPNjun28withtaus2,muonPNjun28norwwithtaus1,muonPNjun28norwwithtaus2,muonPNv2rw1,muonPNv2rw2,muonPNv2norw1,muonPNv2norw2,muonTable) 




