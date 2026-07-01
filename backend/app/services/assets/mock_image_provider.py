"""Mock image provider for local development and testing."""

from app.services.assets.models import AssetPackage


class MockImageProvider:
    """Returns mock image paths without generating real images."""

    def generate(self, package: AssetPackage) -> AssetPackage:
        updated_assets = [
            asset.model_copy(
                update={
                    "metadata": {
                        **asset.metadata,
                        "image_path": f"mock://image/scene-{asset.scene_number}.png",
                    },
                }
            )
            for asset in package.assets
        ]

        return package.model_copy(
            update={
                "assets": updated_assets,
                "provider": "mock",
                "status": "assets_generated",
            }
        )
