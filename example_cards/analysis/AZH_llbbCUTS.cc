#include "Rivet/Analysis.hh"
#include "Rivet/AnalysisHandler.hh"
#include "Rivet/Projections/FinalState.hh"
#include "Rivet/Projections/VetoedFinalState.hh"
#include "Rivet/Projections/PromptFinalState.hh"
#include "Rivet/Projections/LeptonFinder.hh"
#include "Rivet/Projections/IdentifiedFinalState.hh"
#include "Rivet/Projections/VisibleFinalState.hh"
#include "Rivet/Projections/FastJets.hh"
#include "Rivet/Projections/MissingMomentum.hh"
#include "Rivet/Projections/SmearedParticles.hh"
#include "Rivet/Projections/SmearedJets.hh"
#include "Rivet/Projections/SmearedMET.hh"
#include "Rivet/Projections/ChargedFinalState.hh"
#include "Rivet/Projections/UnstableParticles.hh"
#include "Rivet/Projections/InvisibleFinalState.hh"

namespace Rivet {

  class AZH_llbbCUTS : public Analysis {
  public:

    RIVET_DEFAULT_ANALYSIS_CTOR(AZH_llbbCUTS);

    void init() {

      // Do lepton isolation?
      // if ( getOption("LEP_ISO") == "OFF" ) _lep_iso = false;
      if ( getOption("SEL") == "HIGHMBB" ) _HighMbb = true;
 
      // All final state particles
      FinalState fs(Cuts::abseta < 5.0);
      
      // Get photons to dress leptons
      IdentifiedFinalState all_photons(fs);
      all_photons.acceptIdPair(PID::PHOTON);

      IdentifiedFinalState photons(Cuts::abspid == PID::PHOTON, true);
      declare(photons, "photons");

      IdentifiedFinalState electrons(Cuts::abseta < 2.47 && Cuts::pT > 7.*GeV);
      electrons.acceptIdPair(PID::ELECTRON);
      declare(electrons, "Electrons");

      IdentifiedFinalState muons(Cuts::abseta < 2.5 && Cuts::pT > 7.*GeV);
      muons.acceptIdPair(PID::MUON);
      declare(muons, "Muons");

      // for pTmiss
      declare(VisibleFinalState(Cuts::abseta < 4.9), "vfs");
 
      VetoedFinalState vfs;
      vfs.addVetoPairId(PID::MUON);
      vfs.addVetoPairId(PID::ELECTRON);
     
      // small-R jets
      FastJets jets(vfs, JetAlg::ANTIKT, 0.4);
      declare(jets, "Jets");

      // Projection to find MET
      MissingMomentum missmom(Cuts::abseta < 4.9);
      declare(missmom, "MET");

      // Final state including all unstable particles (including taus)
      declare(UnstableParticles(Cuts::abseta < 5. && Cuts::pT > 5.*GeV), "UFS");
      
      // all tracks (to do deltaR with leptons)
      declare(ChargedFinalState(Cuts::abseta < 3. && Cuts::pT > 0.5*GeV), "cfs");

      //// Book histograms

      // Truth
      // book(_h["mH_first"], "mH_first", 400, 0., 2000.);
      // book(_h["mA_first"], "mA_first", 400, 0., 2000.);
      // book(_h["mH_last"], "mH_last", 400, 0., 2000.);
      // book(_h["mA_last"], "mA_last", 400, 0., 2000.);
      // book(_h["mH_firstB"], "mH_firstB", 400, 0., 2000.);
      // book(_h["mA_firstB"], "mA_firstB", 400, 0., 2000.);
      // book(_h["mH_lastB"], "mH_lastB", 400, 0., 2000.);
      // book(_h["mA_lastB"], "mA_lastB", 400, 0., 2000.);

      // Inclusive
      // book(_h["allEvents"],      "allEvents",      1, 0., 1.);
      // book(_h["allEntries"],     "allEntries",     1, 0., 1.);
      // book(_h["CutFlow"],        "CutFlow",        10, 0., 10.);

      book(_h["njets"],          "njets",          10, -0.5, 9.5);
      book(_h["nbjets"],         "nbjets",         7, -0.5, 6.5);

      book(_h["nleptons"],       "nleptons",       7, -0.5, 6.5);

      book(_h["HT"],             "HT",             400, 0., 2000.);
      book(_h["ETmiss"],         "ETmiss",         200, 0., 1000.);
      book(_h["metSig"],         "metSig",         100, 0., 50.);

      book(_h["pT_lep1"],       "pT_lep1",       150, 0., 1500.);
      book(_h["pT_lep2"],       "pT_lep2",       150, 0., 1500.);
      book(_h["eta_lep1"],      "eta_lep1",      100, -5, 5);
      book(_h["eta_lep2"],      "eta_lep2",      100, -5, 5);

      book(_h["pT_b1"],         "pT_b1",         200, 0., 1000.);
      book(_h["pT_b2"],         "pT_b2",         200, 0., 1000.);
      book(_h["eta_b1"],        "eta_b1",        100, -5., 5.);
      book(_h["eta_b2"],        "eta_b2",        100, -5., 5.);

      book(_h["dR_b1b2"],       "dR_b1b2",       50, 0., 5.);
      // book(_h["dphi_b1b2"],     "dphi_b1b2",     32, 0., 3.2);
      
      book(_h["m_ll"],          "m_ll",          200, 0., 1000.);
      book(_h["m_bb"],          "m_bb",          400, 0., 2000.);
      book(_h["m_llbb"],        "m_llbb",        400, 0., 2000.);

      book(_h["pT_ll"],         "pT_ll",         400, 0., 2000.); 
      book(_h["pT_bb"],         "pT_bb",         400, 0., 2000.);
      book(_h["pT_llbb"],       "pT_llbb",       400, 0., 2000.);
      book(_h["J"],             "J",             100, 0., 2.);

      vector<string> btags = {"1tag","2tag","3ptag"}, mHhypos = {};
      if ( _HighMbb ) mHhypos = {"150","200","300","400","500","600","700","800"};
      else mHhypos = {"50","100"};

      // Split into btag and mH bins
      for(auto btag : btags) {
        book(_h["m_llbb_"+btag], "m_llbb_"+btag, 400, 0., 2000.);
        for(auto mHhypo : mHhypos) {
          book(_h["m_llbb_"+btag+"_Hlo"+mHhypo], "m_llbb_"+btag+"_Hlo"+mHhypo, 400, 0., 2000.);
          book(_h["m_llbb_"+btag+"_Hin"+mHhypo], "m_llbb_"+btag+"_Hin"+mHhypo, 400, 0., 2000.);
          book(_h["m_llbb_"+btag+"_Hhi"+mHhypo], "m_llbb_"+btag+"_Hhi"+mHhypo, 400, 0., 2000.);
        }
      }
    }

    void analyze(const Event& event) {

      ++m_nEvents_processed;

      // _h["allEntries"]->fill(0., 1./event.weights()[0]);

      const Jets jets = apply<FastJets>(event, "Jets").jetsByPt(Cuts::pT > 20.*GeV && Cuts::abseta < 2.5);
      const Particles elecs = apply<IdentifiedFinalState>(event, "Electrons").particlesByPt();
      const Particles muons = apply<IdentifiedFinalState>(event, "Muons").particlesByPt();
      const Vector3 miss_mom = apply<MissingMomentum>(event, "MET").vectorEt();

      // get the charged tracks for isolation
      const Particles chg_tracks = apply<ChargedFinalState>(event, "cfs").particles();
      
      // Isolated leptons
      Particles reco_leptons;

      // Electron Isolation 
      Particles reco_e;
      for(auto e : elecs) {
        bool e_near_jet = false;
        for (auto jet : jets){
          if(deltaR(e.momentum(),jet.momentum())<0.4) {
            e_near_jet = true;
            break;
          } 
        }
        if(!e_near_jet) {
          double pTinCone = -e.pT();
          for (auto track : chg_tracks) {
            if(deltaR(e.momentum(),track.momentum())<0.2) {
              pTinCone+=track.pT();
            }
          }
          if(pTinCone<0.1*e.perp()) {
            reco_e.push_back(e);
            reco_leptons.push_back(e);
          } 
        }
      }

      // Muon Isolation 
      Particles reco_mu;
      for(auto mu : muons){
        bool mu_near_jet = false;
        for (auto jet : jets){
          if(deltaR(mu.momentum(),jet.momentum())<0.4){
            mu_near_jet = true;
            break;
          } 
        }
        if(!mu_near_jet){
          double pTinCone = -mu.pT();
          for (auto track : chg_tracks){
            if(deltaR(mu.momentum(),track.momentum())<0.2){
              pTinCone+=track.pT();
            }
          }
          if(pTinCone<0.1*mu.perp()){
            reco_mu.push_back(mu);
            reco_leptons.push_back(mu);
          } 
        }
      }

      //----------------------------------------------------------------------------------------------------
      // Taus
      Particles tau_candidates;
      for (const Particle& tau : apply<UnstableParticles>(event, "UFS").particlesByPt()) {
        // Only pick taus out of all unstable particles
        if (tau.abspid() != PID::TAU) continue;

        // Check that tau has decayed into daughter particles
        if (tau.genParticle()->end_vertex() == 0) continue;

        // Calculate visible tau pT from pT of tau neutrino in tau decay for pT and |eta| cuts
        FourMomentum daughter_tau_neutrino_momentum = get_tau_neutrino_mom(tau);
        Particle tau_vis = tau;
        tau_vis.setMomentum(tau.momentum()-daughter_tau_neutrino_momentum);
        // keep only taus in certain eta region and above 15 GeV of visible tau pT
        if ( tau_vis.pT() <= 15.*GeV || (tau_vis.abseta() > 1.37 && tau_vis.abseta() < 1.52) || tau_vis.abseta() > 2.5) continue;

        // Get prong number (number of tracks) in tau decay and check if tau decays leptonically
        unsigned int nprong = 0;
        bool lep_decaying_tau = false;
        get_prong_number(tau.genParticle(), nprong, lep_decaying_tau);

        // Apply reconstruction efficiency
        // int tau_id = 15;
        // if (nprong == 1) tau_id = 15;
        // else if (nprong == 3) tau_id = 16;

        // Get fiducial lepton efficiency simulate reco efficiency
        // const double eff = (_use_fiducial_lepton_efficiency) ? apply_reco_eff(tau_id, tau_vis) : 1.0;
        const double eff = 1.;
        const bool keep_tau = rand()/static_cast<double>(RAND_MAX) <= eff;

        // Keep tau if nprong = 1, it decays hadronically, and it's reconstructed by the detector
        if ( !lep_decaying_tau && nprong == 1 && keep_tau) tau_candidates.push_back(tau_vis);
      }

      // _h["ntaus"]->fill(tau_candidates.size());

      // tau - electron
      Particles reco_tau;
      for ( const Particle& tau : tau_candidates ) {
        bool away = true;
        // If tau within dR < 0.2 of an electron: remove tau
        for ( const Particle& e : reco_e ) {
          if (deltaR( tau.momentum(), e.momentum()) < 0.2) {
            away = false;
            break;
          }
        }
        // tau - muon
        // If tau within dR < 0.2 of a muon: remove tau
        if (away)  {
          for (const Particle& mu : reco_mu) {
            if (deltaR(tau.momentum(), mu.momentum()) < 0.2) {
              away = false;
              break;
            }
          }
        }
        // If isolated keep it
        if (away) reco_tau.push_back(tau);
      }
      // _h["ntaus_iso"]->fill(reco_tau.size());

      //----------------------------------------------------------------------------------------------------

      Jets bjets, ljets;
      Jets jets_sorted; // first all bjets, then ljets
      double HT = 0., HT2 = 0.;
      for (Jet jet : jets) {
        // tight MET 
        if (jet.abseta()>2.4 && jet.pT()<30.*GeV) vetoEvent;

        HT += jet.pT();
        HT2 += jet.pT2();
        if ( jet.bTagged(Cuts::pT > 5.*GeV) ) bjets += jet;
        else ljets += jet;
      }
      for (Jet bjet : bjets) jets_sorted += bjet;
      for (Jet ljet : ljets) jets_sorted += ljet;

      for (const Particle& lep : reco_leptons){
        HT += lep.pT();
        HT2 += lep.pT2();
      }
   
      double etmiss = miss_mom.perp();
      
      // double dPhib1b2 = 0.;
      double dRb1b2 = 0., J = 0.; 

      // H and A candidates
      double m_ll = 0., m_bb = 0., m_llbb = 0.;
      double pT_ll = 0., pT_bb = 0., pT_llbb = 0.;

      if(jets_sorted.size()>=2 && reco_leptons.size()>=2) {
        // dPhib1b2 = deltaPhi(jets_sorted.at(0), jets_sorted.at(1));
        dRb1b2 = deltaR(jets_sorted.at(0).momentum(),jets_sorted.at(1).momentum());

        FourMomentum Zcand = reco_leptons.at(0).momentum() + reco_leptons.at(1).momentum();
        m_ll = Zcand.mass();
        pT_ll = Zcand.pT();

        FourMomentum HCand = jets_sorted.at(0).momentum() + jets_sorted.at(1).momentum();
        m_bb = HCand.mass();
        pT_bb = HCand.pT();

        FourMomentum ACand = Zcand + HCand;
        m_llbb = ACand.mass();
        pT_llbb = ACand.pT();

        J = sqrt(HT2)/m_llbb;
      }

      //----------------------------------------------------------------------------------------------------
      // Truth particles

      // Particle AbosonFirst, AbosonLast, HbosonFirst, HbosonLast, ZbosonFirst, ZbosonLast;
      // findFirstParticleById(AbosonFirst, event, 36);
      // findFirstParticleById(HbosonFirst, event, 35);
      // findFirstParticleById(ZbosonFirst, event, 23);
      // findLastParticleById(AbosonLast, event, 36);
      // findLastParticleById(HbosonLast, event, 35);
      // findLastParticleById(ZbosonLast, event, 23);
      // double mH = HbosonFirst.mass();

      //// Find the first/last b-quarks from the Higgs

      // Particles bFromHbosonFirst, bFromHbosonLast;
      // findFirstParticlesFromDecay(HbosonLast, bFromHbosonFirst, PID::BQUARK);
      // findLastParticlesFromDecay(HbosonLast, bFromHbosonLast, PID::BQUARK);

      // FourMomentum AbosonFirstB, AbosonLastB, HbosonFirstB, HbosonLastB;
      // HbosonFirstB = bFromHbosonFirst.at(0).momentum()+bFromHbosonFirst.at(1).momentum();
      // HbosonLastB = bFromHbosonLast.at(0).momentum()+bFromHbosonLast.at(1).momentum();
      // AbosonFirstB = HbosonFirstB + ZbosonFirst;
      // AbosonLastB = HbosonLastB + ZbosonLast;

      //----------------------------------------------------------------------------------------------------
      //// Cuts
      
      bool passPreSelection = false, passSelection = false;
      bool njet_geq2 = false, nbjet_geq1 = false, nlep_eq2 = false, lep1_pT_gtr27 = false, isOSSF = false, mZwindow = false;
      bool bjet1_pT_gtr45 = false, metSigcut = false, Jcut = false;
      bool leptons_pT_gtr18 = false; // NEW


      // pre-selection
      njet_geq2 = jets.size() >= 2;
      nbjet_geq1 = bjets.size() >= 1;
      nlep_eq2 = reco_leptons.size() == 2;

      passPreSelection = njet_geq2 && nbjet_geq1 && nlep_eq2;

      if(passPreSelection) {
        // selection
        // lep1_pT_gtr27 = reco_leptons.at(0).pT() > 27.*GeV;
	leptons_pT_gtr18 = reco_leptons.at(0).pT() > 18.*GeV && reco_leptons.at(1).pT() > 18.*GeV; // NEW

        isOSSF = reco_leptons.at(0).pid() == -reco_leptons.at(1).pid();
        // mZwindow = fabs(m_ll - 91.1876*GeV) < 10.*GeV;
        bjet1_pT_gtr45 = jets_sorted.at(0).pT() > 45.*GeV; // Ask tetiana why this is here. Should be here for >>mh2
        metSigcut = etmiss/std::sqrt(HT) < 3.5*std::sqrt(GeV); // event-level metSig
        Jcut = J > 0.4; // Does this make sense for small masses? For leptons we expect to not use that as we re looking for off shells with small P

        // passSelection = isOSSF && lep1_pT_gtr27 && mZwindow && metSigcut && Jcut && leptons_pT_gtr18;
        passSelection = isOSSF &&  metSigcut && Jcut && leptons_pT_gtr18;
	// passSelection = true;
        if ( _HighMbb ) passSelection = passSelection && bjet1_pT_gtr45;
      }

      // _h["allEvents"]->fill(0.);

      // if(passPreSelection) {
      if(passSelection) {
        _h["njets"]->fill(jets.size());
        _h["nbjets"]->fill(bjets.size());
        _h["nleptons"]->fill(reco_e.size()+reco_mu.size()); // <- isolated, non-isolated: elecs.size()+muons.size()

        _h["pT_lep1"]->fill(reco_leptons.at(0).pT()*GeV);
        _h["pT_lep2"]->fill(reco_leptons.at(1).pT()*GeV);
        _h["eta_lep1"]->fill(reco_leptons.at(0).eta());
        _h["eta_lep2"]->fill(reco_leptons.at(1).eta());

        _h["pT_b1"]->fill(jets_sorted.at(0).pT()*GeV);
        _h["pT_b2"]->fill(jets_sorted.at(1).pT()*GeV);
        _h["eta_b1"]->fill(jets_sorted.at(0).eta());
        _h["eta_b2"]->fill(jets_sorted.at(1).eta());

        _h["HT"]->fill(HT*GeV);
        _h["ETmiss"]->fill(etmiss*GeV);
        _h["metSig"]->fill(etmiss/std::sqrt(HT)*std::sqrt(GeV));
        _h["dR_b1b2"]->fill(dRb1b2);
        // _h["dphi_b1b2"]->fill(dPhib1b2);

        _h["m_ll"]->fill(m_ll*GeV);
        _h["m_bb"]->fill(m_bb*GeV);
        _h["m_llbb"]->fill(m_llbb*GeV);

        _h["pT_ll"]->fill(pT_ll*GeV);
        _h["pT_bb"]->fill(pT_bb*GeV);
        _h["pT_llbb"]->fill(pT_llbb*GeV);

        _h["J"]->fill(J);

        // Fill m_llbb split into btag regions and mH bins
        string btag = "", mHbin = "";
        double mHwin_low = -99, mHwin_high = -99, reso = 1.;

        if ( bjets.size()==1 ) {
          btag = "1tag";
          reso = ( _HighMbb ) ? 0.15 : 0.25;
        } else if ( bjets.size()==2 ) {
          btag = "2tag";
          reso = 0.15;
        } else {
          btag = "3ptag";
          reso = 0.20;
        }

        _h["m_llbb_"+btag]->fill(m_llbb*GeV);

        vector<int> mHhypos;
        if ( _HighMbb ) mHhypos = {150,200,300,400,500,600,700,800};
        else mHhypos = {50,100};

        // Split into btag and mH bins
        for(auto mHhypo : mHhypos) {

          mHwin_low  = (2.5*reso*mHhypo > 20) ? 2.5*reso*mHhypo : 20;
          mHwin_high = (1.0*reso*mHhypo > 20) ? 1.0*reso*mHhypo : 20;

          if (m_bb*GeV < mHhypo - mHwin_low) mHbin = "Hlo";
          else if((m_bb*GeV >= mHhypo - mHwin_low) && (m_bb*GeV <= mHhypo + mHwin_high)) mHbin = "Hin";
          else if (m_bb*GeV > mHhypo + mHwin_high) mHbin = "Hhi";

          _h["m_llbb_"+btag+"_"+mHbin+to_string(mHhypo)]->fill(m_llbb*GeV);
        }
      }

      // Truth
      // _h["mH_first"]->fill(HbosonFirst.mass()*GeV);
      // _h["mA_first"]->fill(AbosonFirst.mass()*GeV);
      // _h["mH_last"]->fill(HbosonLast.mass()*GeV);
      // _h["mA_last"]->fill(AbosonLast.mass()*GeV);

      // _h["mH_firstB"]->fill(HbosonFirstB.mass()*GeV);
      // _h["mA_firstB"]->fill(AbosonFirstB.mass()*GeV);
      // _h["mH_lastB"]->fill(HbosonLastB.mass()*GeV);
      // _h["mA_lastB"]->fill(AbosonLastB.mass()*GeV);

      // CutFlow
      // if (mH <= 150.*GeV) {

      //   // low mass
      //   _h["CutFlow"]->fill(0.);               // pT_lep > 7 GeV, eta_el|mu < 2.47|2.50, pT_bjet > 20 GeV, eta_bjet < 2.5 --- Object selection ---
      //   if(nbjet_geq2) {
      //     _h["CutFlow"]->fill(1.);             // nbjet >= 2
      //     if(nlep_geq2) {
      //       _h["CutFlow"]->fill(2.);           // nlep >= 2  --- Pre-selection ---
      //       if(isOSSF) {
      //         _h["CutFlow"]->fill(3.);         // OSSF
      //         if(lep1_pT_gtr27) {
      //           _h["CutFlow"]->fill(4.);       // pT_lep1 > 27 GeV
      //           if(mZwindow) {
      //             _h["CutFlow"]->fill(5.);     // mZwindow
      //             if(metSigcut) {
      //               _h["CutFlow"]->fill(6.);   // ETmiss/sqrt(HT) < 3.5 GeV^1/2
      //               if(Jcut) {
      //                 _h["CutFlow"]->fill(7.); // sqrt(sum(pT^2))/m_llbb > 0.3 (mH < 200 GeV)
      //               }
      //             }
      //           }
      //         }
      //       }
      //     }
      //   }

      // } else {

      //   // high mass
      //   _h["CutFlow"]->fill(0.);                 // pT_lep > 7 GeV, eta_el|mu < 2.47|2.50, pT_bjet > 20 GeV, eta_bjet < 2.5 --- Object selection ---
      //   if(nbjet_geq2) {
      //     _h["CutFlow"]->fill(1.);               // nbjet >= 2
      //     if(nlep_geq2) {
      //       _h["CutFlow"]->fill(2.);             // nlep >= 2  --- Pre-selection ---
      //       if(isOSSF) {
      //         _h["CutFlow"]->fill(3.);           // OSSF
      //         if(lep1_pT_gtr27) {
      //           _h["CutFlow"]->fill(4.);         // pT_lep1 > 27 GeV
      //           if(mZwindow) {
      //             _h["CutFlow"]->fill(5.);       // mZwindow
      //             if(bjet1_pT_gtr45) {
      //               _h["CutFlow"]->fill(6.);     // pT_bjet1 > 45 GeV (mH > 150 GeV)
      //               if(metSigcut) {
      //                 _h["CutFlow"]->fill(7.);   // ETmiss/sqrt(HT) < 3.5 GeV^1/2
      //                 if(Jcut) {
      //                   _h["CutFlow"]->fill(8.); // sqrt(sum(pT^2))/m_llbb > 0.4 (mH >= 200 GeV)
      //                 }
      //               }
      //             }
      //           }
      //         }
      //       }
      //     }
      //   }

      // }      
    }

    void finalize() {
      // for (const auto &hit : _h) {
      //   double sf = 1.0;
      //   if (hit.first != "CutFlow") normalize(hit.second, sf);
      // }
      // Normalize to cross-section
      // const double sf = (crossSection() / sumOfWeights());
      // for (auto hist : _h) {
      //   scale(hist.second, sf);
      // }
    }

    void findFirstParticleById(Particle &part, const Event & event, const int id) {
      const GenEvent *genEvent = event.genEvent();
      const vector<ConstGenParticlePtr> genParticles = HepMCUtils::particles(genEvent);
      for (auto p : genParticles) {
        if ( p->pdg_id() == id) {
          part = Particle(p);
          break;
        }
      }
    }

    void findLastParticleById(Particle &part, const Event & event, const int id) {
      const GenEvent *genEvent = event.genEvent();
      const vector<ConstGenParticlePtr> genParticles = HepMCUtils::particles(genEvent);
      for (auto p : genParticles) {
        if (p->pdg_id() == id) {
          bool isLast = true;
          ConstGenVertexPtr dv = p->end_vertex();
          if (dv != nullptr) {
            // Loop over all daughter particles and check if they contain a particle with the same pdg id
            for(ConstGenParticlePtr pp: HepMCUtils::particles(dv, Relatives::CHILDREN)){
              if (abs(pp->pdg_id()) == id) isLast = false;
            }
          }
          if (isLast){
            part = Particle(p);
          }
        }
      }
    }

    void findFirstParticlesFromDecay(const Particle &mother, Particles &daughters, const int daughterId) {
      ConstGenVertexPtr dv = mother.genParticle()->end_vertex();
      for(ConstGenParticlePtr pp: HepMCUtils::particles(dv, Relatives::CHILDREN)){
        if (abs(pp->pdg_id()) == daughterId) daughters.push_back(Particle(pp));
      }
    }
    
    void findLastParticlesFromDecay(const Particle &mother, Particles &daughters, const int daughterId) {
      ConstGenVertexPtr dv = mother.genParticle()->end_vertex();
      for(ConstGenParticlePtr pp: HepMCUtils::particles(dv, Relatives::CHILDREN)){
        if (abs(pp->pdg_id()) == daughterId) {
          ConstGenParticlePtr lastDaughter = pp;
          while ( !isLastInChain(lastDaughter) ) {
            ConstGenVertexPtr dv2 = lastDaughter->end_vertex();
            for(ConstGenParticlePtr pp2: HepMCUtils::particles(dv2, Relatives::CHILDREN)){\
              if ( pp2->pdg_id() == lastDaughter->pdg_id() ) {
                lastDaughter = pp2;
              }
            }
          }
          daughters.push_back(lastDaughter);
        }
      }
    }

    bool isLastInChain(ConstGenParticlePtr p) {
      bool isLast = true;
      ConstGenVertexPtr dv = p->end_vertex();
      for(ConstGenParticlePtr pp: HepMCUtils::particles(dv, Relatives::CHILDREN)){
        if ( pp->pdg_id() == p->pdg_id() ) { isLast = false; break; }
      }
      return isLast;
    }

    /// Function returning 4-vector of daughter-particle if it is a tau neutrino
    FourMomentum get_tau_neutrino_mom(const Particle& p)  {
      assert(p.abspid() == PID::TAU);
      ConstGenVertexPtr dv = p.genParticle()->end_vertex();
      assert(dv != nullptr);
      for(ConstGenParticlePtr pp: HepMCUtils::particles(dv, Relatives::CHILDREN)){
        if (abs(pp->pdg_id()) == PID::NU_TAU) return FourMomentum(pp->momentum());
      }
      return FourMomentum();
    }

    /// Function calculating the prong number of taus
    void get_prong_number(ConstGenParticlePtr p, unsigned int& nprong, bool& lep_decaying_tau) {
      assert(p != nullptr);
      //const int tau_barcode = p->barcode();
      ConstGenVertexPtr dv = p->end_vertex();
      assert(dv != nullptr);
      for(ConstGenParticlePtr pp: HepMCUtils::particles(dv, Relatives::CHILDREN)){
        // If they have status 1 and are charged they will produce a track and the prong number is +1
        if (pp->status() == 1)  {
          const int id = pp->pdg_id();
          if (Rivet::PID::charge(id) != 0 ) ++nprong;
          // Check if tau decays leptonically
          // @todo Can a tau decay include a tau in its decay daughters?!
          if ((abs(id) == PID::ELECTRON || abs(id) == PID::MUON || abs(id) == PID::TAU) && abs(p->pdg_id()) == PID::TAU) lep_decaying_tau = true;
        }
        // If the status of the daughter particle is 2 it is unstable and the further decays are checked
        else if (pp->status() == 2)  {
          get_prong_number(pp, nprong, lep_decaying_tau);
        }
      }
    }

  private:

    /// @name Objects that are used by the event selection decisions
    map<string, Histo1DPtr> _h;
    int m_nEvents_processed = 0;
    // bool _lep_iso = true;
    bool _HighMbb = false;

    // AnalysisHandler handler;
    // handler.skipMultiWeights(true);
  };


  // The hook for the plugin system
  RIVET_DECLARE_PLUGIN(AZH_llbbCUTS);

}
