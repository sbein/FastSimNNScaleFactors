#include <fstream>
#include <iostream>
#include <iomanip>
#include <cmath>
#include <map>
#include <string>

#include "lwtnn/LightweightNeuralNetwork.hh"
#include "lwtnn/parse_json.hh"

static constexpr double PT_EPS  = 1e-4;
static constexpr double ISO_EPS = 1e-6;

static double safe_log10(double x, double eps) {
  return std::log10(std::max(x, eps));
}

static double get(const std::map<std::string, double>& m, const std::string& k) {
  auto it = m.find(k);
  if (it == m.end()) throw std::runtime_error("Missing output key: " + k);
  return it->second;
}

int main(int argc, char** argv) {
  if (argc != 2) {
    std::cerr << "Usage: " << argv[0] << " model.lwtnn.json\n";
    return 1;
  }

  const std::string json_path = argv[1];
  std::ifstream in(json_path);
  if (!in) {
    std::cerr << "ERROR: cannot open " << json_path << "\n";
    return 2;
  }

  auto cfg = lwt::parse_json(in);
  lwt::LightweightNeuralNetwork nn(cfg.inputs, cfg.layers, cfg.outputs);

  // Mock "GEN-matched" electron values (replace with real NanoAOD lookup later)
  const double gen_pt  = 15.0;
  const double gen_eta = 0.4;
  const double gen_phi = 2.1;
  const double gen_iso = 1e-3;

  const double pt_log10  = safe_log10(gen_pt,  PT_EPS);
  const double iso_log10 = safe_log10(gen_iso, ISO_EPS);

  lwt::ValueMap inputs;
  inputs["pt_log10"]  = pt_log10;
  inputs["eta"]       = gen_eta;
  inputs["phi"]       = gen_phi;
  inputs["iso_log10"] = iso_log10;

  const auto out = nn.compute(inputs);

  const double p11 = get(out, "p11");
  const double p10 = get(out, "p10");
  const double p01 = get(out, "p01");
  const double p00 = get(out, "p00");

  const double eff_fast = p11 + p10;
  const double eff_full = p11 + p01;
  const double sf = (eff_fast > 0.0) ? (eff_full / eff_fast) : 0.0;

  std::cout << std::setprecision(17);
  std::cout << "p11 " << p11 << "\n";
  std::cout << "p10 " << p10 << "\n";
  std::cout << "p01 " << p01 << "\n";
  std::cout << "p00 " << p00 << "\n";
  std::cout << "eff_fast " << eff_fast << "\n";
  std::cout << "eff_full " << eff_full << "\n";
  std::cout << "sf_fullOverFast " << sf << "\n";

  return 0;
}
