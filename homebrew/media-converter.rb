# Documentation: https://docs.brew.sh/Formula-Cookbook
#                https://rubydoc.brew.sh/Formula
class MediaConverter < Formula
  include Language::Python::Virtualenv

  desc "Robust media conversion engine for repairing and encoding legacy video formats"
  homepage "https://github.com/paruff/converter"
  url "https://github.com/paruff/converter/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "PLACEHOLDER_SHA256"
  license "MIT"
  head "https://github.com/paruff/converter.git", branch: "main"

  depends_on "python@3.12"
  depends_on "ffmpeg"

  resource "tqdm" do
    url "https://files.pythonhosted.org/packages/source/t/tqdm/tqdm-4.66.0.tar.gz"
    sha256 "d302b3c5b53d47bce91fea46679d9c3c6508cf6332229aa1e7d8653723793386"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/converter", "--version"
    assert_match "Media Converter", shell_output("#{bin}/converter --help")
  end
end
