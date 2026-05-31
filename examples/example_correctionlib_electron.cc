#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

#include "TFile.h"
#include "TTreeReader.h"
#include "TTreeReaderArray.h"
#include "correction.h"

double sf_from_kinematics(const correction::Correction::Ref& corr, double pt, double eta, double phi, double iso) {
  return corr->evaluate(std::vector<correction::Variable::Type>{pt, eta, phi, iso});
}

double sf_from_gen_index(const correction::Correction::Ref& corr, int gen_index, const TTreeReaderArray<float>& GenPart_pt, const TTreeReaderArray<float>& GenPart_eta, const TTreeReaderArray<float>& GenPart_phi, const TTreeReaderArray<float>& GenPart_iso) {
  if (gen_index < 0 || gen_index >= GenPart_pt.GetSize()) return 1.0;
  return sf_from_kinematics(corr, GenPart_pt[gen_index], GenPart_eta[gen_index], GenPart_phi[gen_index], GenPart_iso[gen_index]);
}

int main() {
  const std::string payload = "payloads/Run3_NanoAODv15_correctionlib/EGM/Electron/eff_classifier_pMSSM_334_105076_GenElectron_loose.correctionlib.json";
  const std::string correction_name = "fastsim_sf_pMSSM_334_105076_GenElectron_loose";
  const std::string tiny_nano = "examples/data/ttbar_fastsim_nano_3events.root";

  auto cset = correction::CorrectionSet::from_file(payload);
  auto corr = cset->at(correction_name);

  TFile nano_file(tiny_nano.c_str());
  TTreeReader events("Events", &nano_file);
  TTreeReaderArray<short> Electron_genPartIdx(events, "Electron_genPartIdx");
  TTreeReaderArray<float> GenPart_pt(events, "GenPart_pt");
  TTreeReaderArray<float> GenPart_eta(events, "GenPart_eta");
  TTreeReaderArray<float> GenPart_phi(events, "GenPart_phi");
  TTreeReaderArray<float> GenPart_iso(events, "GenPart_iso");

  std::cout << std::setprecision(17);
  int event_index = 0;
  while (events.Next()) {
    // Analyst chooses collection, applies ID/isolation/selection cuts, then gets the SF.
    for (int electron_index = 0; electron_index < Electron_genPartIdx.GetSize(); ++electron_index) {
      const int gen_index = Electron_genPartIdx[electron_index];
      const double sf = sf_from_gen_index(corr, gen_index, GenPart_pt, GenPart_eta, GenPart_phi, GenPart_iso);
      std::cout << "event " << event_index << " electron " << electron_index << ": sf_full_over_fast " << sf << "\n";
    }
    ++event_index;
  }

  const double sf_scan = sf_from_kinematics(corr, 15.0, 0.4, 2.1, 1e-3);
  std::cout << "kinematic scan point: sf_full_over_fast " << sf_scan << "\n";
  return 0;
}
