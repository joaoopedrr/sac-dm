import styled from "styled-components";

export const Container = styled.div`
  width: 100%;
  display: flex;
  justify-content: center;
  flex-direction: column;
  align-items: center;

  .apexcharts-tooltip {
    background-color: ${({ theme }) => theme.gray900} !important;
  }

  .apexcharts-tooltip-title {
    background-color: ${({ theme }) => theme.gray900} !important;
  }

  .apexcharts-theme-light,
  .apexcharts-active {
    border: none;
  }

  .apexcharts-menu {
    background-color: ${({ theme }) => theme.gray900};

    .apexcharts-menu-item {
      color: ${({ theme }) => theme.grayChateau};

      &:hover {
        background-color: ${({ theme }) => theme.grayChateau};
        color: ${({ theme }) => theme.gray900};
      }
    }
  }
`;

export const ButtonContainer = styled.div`
  margin-bottom: 20px;
  display: flex;
  gap: 10px; /* Espaço horizontal entre os botões */
`;

export const StyledButton = styled.button`
  background-color: ${({ theme }) => theme.gray900};
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;

  &:hover {
    background-color: ${({ theme }) => theme.gray800}; /* Cinza mais escuro */
  }
`;
