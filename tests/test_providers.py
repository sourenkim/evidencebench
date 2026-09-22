from evidencebench.providers import EmbeddingProvider, LLMProvider, ProviderConfiguration


def test_provider_protocols_are_importable_without_vendor_sdks() -> None:
    assert LLMProvider is not None
    assert EmbeddingProvider is not None
    config = ProviderConfiguration("fake", "test-model", data_sent_remotely=False)
    assert config.data_sent_remotely is False
