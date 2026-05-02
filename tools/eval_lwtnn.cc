#include <fstream>
#include <iostream>
#include <map>
#include <string>

#include "lwtnn/LightweightNeuralNetwork.hh"
#include "lwtnn/parse_json.hh"
#include <iomanip>

int main(int argc, char** argv) {
  if (argc != 1 + 1 + 4) {
    std::cerr << "Usage: " << argv[0] << " model.json pt_log10 eta phi iso_log10\n";
    return 1;
  }

  const std::string json_path = argv[1];
  const double pt_log10  = std::stod(argv[2]);
  const double eta     = std::stod(argv[3]);
  const double phi     = std::stod(argv[4]);
  const double iso_log10 = std::stod(argv[5]);

  std::ifstream in(json_path);
  if (!in) {
    std::cerr << "ERROR: cannot open " << json_path << "\n";
    return 2;
  }

  auto cfg = lwt::parse_json(in);
  lwt::LightweightNeuralNetwork nn(cfg.inputs, cfg.layers, cfg.outputs);

  lwt::ValueMap inputs;
  inputs["pt_log10"]  = pt_log10;
  inputs["eta"]     = eta;
  inputs["phi"]     = phi;
  inputs["iso_log10"] = iso_log10;
  std::cout << std::setprecision(17);
  auto out = nn.compute(inputs);
  for (const auto& kv : out) {
    std::cout << kv.first << " " << kv.second << "\n";
  }
  return 0;
}
