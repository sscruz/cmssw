#include <string>

#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/Exception.h"

#include "DataFormats/ParticleFlowCandidate/interface/PFCandidate.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidateFwd.h"
#include "DataFormats/PatCandidates/interface/MuonTrack.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackExtraFwd.h"
#include "DataFormats/Common/interface/RefToPtr.h"
#include "DataFormats/Math/interface/libminifloat.h"
#include "DataFormats/Math/interface/Point3D.h"

#include "MagneticField/Engine/interface/MagneticField.h"
#include "CommonTools/Utils/interface/StringCutObjectSelector.h"




namespace pat {

  class PATMuonTrackProducer : public edm::stream::EDProducer<> {
  public:
    typedef pat::MuonTrack::LorentzVector LorentzVector;

    explicit PATMuonTrackProducer(const edm::ParameterSet&);
    ~PATMuonTrackProducer() override;

    void produce(edm::Event&, const edm::EventSetup&) override;

  private:
    const edm::EDGetTokenT<reco::TrackCollection> gtrk_;
    const edm::EDGetTokenT<pat::MuonCollection> mu_;
    const edm::EDGetTokenT<reco::PFCandidateCollection> pfcands_;
    const edm::EDGetTokenT<edm::Association<pat::PackedCandidateCollection>> pf_to_pc_;
    const StringCutObjectSelector<reco::Track> trk_selection_;

//  const float pT_cut_; 
//const float abs_eta_cut_;

  };
}  // namespace pat

pat::PATMuonTrackProducer::PATMuonTrackProducer(const edm::ParameterSet& iConfig)
  :   gtrk_(consumes<reco::TrackCollection>(iConfig.getParameter<edm::InputTag>("generalTracks"))),
      mu_(consumes<pat::MuonCollection>(iConfig.getParameter<edm::InputTag>("slimmedMuons"))),
      pfcands_(consumes<reco::PFCandidateCollection>(iConfig.getParameter<edm::InputTag>("pfCandidates"))),
      pf_to_pc_(consumes<edm::Association<pat::PackedCandidateCollection>>(iConfig.getParameter<edm::InputTag>("packedCandidates"))),
      trk_selection_(iConfig.getParameter<std::string>("trk_selection"))
{
  produces<pat::MuonTrackCollection>();

}

pat::PATMuonTrackProducer::~PATMuonTrackProducer() {}

void pat::PATMuonTrackProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {

  // generalTracks collection
  edm::Handle<reco::TrackCollection> gtrk;
  iEvent.getByToken(gtrk_, gtrk);
  //pf candidate collection
  edm::Handle<reco::PFCandidateCollection> pfcands;
  iEvent.getByToken(pfcands_,pfcands);
  // pf cand. association to packed cand.
  edm::Handle<edm::Association<pat::PackedCandidateCollection>> pf_to_pc;
  iEvent.getByToken(pf_to_pc_,pf_to_pc);

  // slimmedMuons collection
  edm::Handle<pat::MuonCollection> muons;
  iEvent.getByToken(mu_, muons);

  auto outPtrP = std::make_unique<std::vector<pat::MuonTrack>>( );
  outPtrP->reserve(gtrk->size());

  // create associations between muon
  std::vector<unsigned> trk_to_pc(gtrk->size(),pfcands->size());
  for (unsigned ipf=0; ipf<pfcands->size(); ++ipf){
    edm::Ref<reco::PFCandidateCollection> refcand(pfcands,ipf);
    const reco::PFCandidate& pfcand= pfcands->at(ipf);
    auto packed_ref = (*pf_to_pc)[refcand];
    if (pfcand.charge() && pfcand.trackRef().isNonnull() && packed_ref.isNonnull() && pfcand.trackRef().id() == gtrk.id() )
        trk_to_pc[pfcand.trackRef().index()] = ipf;
  }

  std::vector<unsigned> trk_to_mu(gtrk->size(),muons->size());
  for (unsigned imu=0; imu<muons->size(); ++imu){
    const pat::Muon & muon = (*muons)[imu];
    pat::MuonRef muonRef(muons,imu);
    if (muon.track().isNonnull() )
       trk_to_mu[muon.track().index()] = imu;
  }

 
  
  for (unsigned int igt = 0; igt < gtrk->size(); igt++) {
    const reco::Track& trk = (*gtrk)[igt];
    if (!trk_selection_(trk)) continue;   
 
    pat::PackedCandidateRef refcand;
    if (trk_to_pc[igt]!=pfcands->size()){
      edm::Ref<reco::PFCandidateCollection> pfcand(pfcands,trk_to_pc[igt]);
      refcand = (*pf_to_pc)[pfcand];
     }

    pat::MuonRef muonRef;    
    if (trk_to_mu[igt]!=muons->size()){
      muonRef = edm::Ref<pat::MuonCollection>(muons,trk_to_mu[igt]);
    }

    LorentzVector p4;
    double m = 0.105;  //assume muon mass
    double E = sqrt(m * m + trk.p() * trk.p());
    p4.SetPxPyPzE(
       MiniFloatConverter::reduceMantissaToNbitsRounding<12>(trk.px()),
       MiniFloatConverter::reduceMantissaToNbitsRounding<12>(trk.py()),
       MiniFloatConverter::reduceMantissaToNbitsRounding<12>(trk.pz()),
       MiniFloatConverter::reduceMantissaToNbitsRounding<12>(E)
                 );
    
    auto cov = trk.covariance();
    for (size_t i=0; i<5; ++i) {
      for ( size_t j=i; j<5; ++j)
        cov(i,j)=MiniFloatConverter::reduceMantissaToNbitsRounding<12>(cov(i,j));
    }



  math::XYZPoint refpoint(
			    MiniFloatConverter::reduceMantissaToNbitsRounding<12>(trk.referencePoint().X()),
                            MiniFloatConverter::reduceMantissaToNbitsRounding<12>(trk.referencePoint().Y()),
                            MiniFloatConverter::reduceMantissaToNbitsRounding<12>(trk.referencePoint().Z())
			    );
 //   pat::PackedCandidateRef ref(pfcands,0);
    
    outPtrP->emplace_back(pat::MuonTrack(p4,
				      refpoint,
				      trk.charge(),
				      cov,
				      muonRef,
                                      refcand
				      ));

  }
  auto orphHandle = iEvent.put(std::move(outPtrP));

}






using pat::PATMuonTrackProducer;
#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(PATMuonTrackProducer);
